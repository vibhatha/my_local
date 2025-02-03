import sys
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from mylocalstats.population_stats.models import Region, TotalPopulation
from tqdm import tqdm


class Command(BaseCommand):
    """Insert total population data from TSV file into the database.

    This command processes a TSV file containing total population data and links it
    to existing regions in the database. Only processes records where the entity_id
    matches an existing region of the specified type.

    Examples:
        Insert population data for states in year 2018:
            >>> python manage.py insert_total_population /path/to/population.tsv --year 2018 --region-type state
        
        Insert population data for counties in year 2020:
            >>> python manage.py insert_total_population /path/to/population.tsv --year 2020 --region_type county

    Arguments:
        file_path: Path to the TSV file containing population data
        --year: Year of the population data (default: 2012)
        --region-type: Type of regions to process (e.g., 'state', 'county')

    TSV Format Expected:
        entity_id    total_population
        P001        2500000
        P002        1800000
        ...
    """

    help = "Insert total population data from TSV"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to the TSV file")
        parser.add_argument(
            "--year",
            type=int,
            default=2012,
            help="Year of the population data (default: 2012)"
        )
        parser.add_argument(
            "--region_type",
            type=str,
            required=True,
            help="Type of regions to process (e.g., 'state', 'county')"
        )

    def handle(self, *args, **options):
        file_path = options["file_path"]
        year = options["year"]
        region_type = options["region_type"]

        try:
            # Use sep='\t' for TSV files
            data = pd.read_csv(file_path, sep='\t')
            total_rows = len(data)

            # Get existing region IDs only for the specified region type
            existing_region_ids = set(
                Region.objects.filter(type=region_type)
                .values_list('entity_id', flat=True)
            )
            
            self.stdout.write(
                f"Found {len(existing_region_ids)} existing {region_type} regions in database"
            )
            self.stdout.write(f"Starting import for {total_rows} population records for year {year}...")

            # Statistics for reporting
            processed_count = 0
            skipped_count = 0
            invalid_count = 0

            # Use transaction to ensure data consistency
            with transaction.atomic():
                # Create progress bar
                for index, row in tqdm(data.iterrows(), total=total_rows, desc="Importing population data"):
                    entity_id = row["entity_id"]
                    
                    # Skip if region doesn't exist
                    if entity_id not in existing_region_ids:
                        skipped_count += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"\nSkipping {entity_id}: Region does not exist in database"
                            )
                        )
                        continue

                    # Process population value
                    try:
                        total_population = pd.to_numeric(
                            str(row["total_population"]).replace(",", ""), 
                            errors="coerce"
                        )
                    except (ValueError, TypeError):
                        invalid_count += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"\nSkipping {entity_id}: Invalid population value"
                            )
                        )
                        continue

                    # Skip if population is not a valid number
                    if pd.isna(total_population):
                        invalid_count += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"\nSkipping {entity_id}: Invalid population value"
                            )
                        )
                        continue

                    try:
                        # Get the region (we know it exists, but get it for the relation)
                        region = Region.objects.get(entity_id=entity_id)

                        # Create or update total population
                        TotalPopulation.objects.update_or_create(
                            region=region,
                            defaults={
                                "total_population": int(total_population),
                                "year": year
                            }
                        )
                        processed_count += 1

                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"\nError processing {entity_id}: {str(e)}"
                            )
                        )
                        continue

            # Final report
            self.stdout.write("\nImport Summary:")
            self.stdout.write(f"Total records in file: {total_rows}")
            self.stdout.write(f"Successfully processed: {processed_count}")
            self.stdout.write(f"Skipped (no matching region): {skipped_count}")
            self.stdout.write(f"Skipped (invalid population): {invalid_count}")
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nSuccessfully imported population data for year {year}. "
                    f"Processed {processed_count} out of {total_rows} records."
                )
            )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
        except pd.errors.EmptyDataError:
            self.stdout.write(self.style.ERROR("The TSV file is empty"))
        except KeyError as e:
            self.stdout.write(self.style.ERROR(f"Missing required column: {str(e)}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {str(e)}"))
