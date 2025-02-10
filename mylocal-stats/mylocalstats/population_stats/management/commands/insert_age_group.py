import sys
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from mylocalstats.population_stats.models import Region, AgeDistribution
from tqdm import tqdm

class Command(BaseCommand):
    """Insert age distribution data from TSV file into the database.

    This command processes a TSV file containing age group distribution data and links it
    to existing regions in the database. Only processes records where the entity_id
    matches an existing region of the specified type.

    Examples:
        Insert age distribution data for states in year 2018:
            >>> python manage.py insert_age_group /path/to/age_group.tsv --year 2018 --region-type state
        
        Insert age distribution data for counties in year 2020:
            >>> python manage.py insert_age_group /path/to/age_group.tsv --year 2020 --region_type county

    Arguments:
        file_path: Path to the TSV file containing age distribution data
        --year: Year of the data (default: 2012)
        --region-type: Type of regions to process (e.g., 'state', 'county')

    TSV Format Expected:
        entity_id    less_than_10    10_~_19    20_~_29    ...    90_and_above
        P001        250000          200000     180000      ...    5000
        P002        180000          160000     140000      ...    3000
        ...
    """

    help = "Insert age distribution data from TSV"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to the TSV file")
        parser.add_argument(
            "--year",
            type=int,
            default=2012,
            help="Year of the age distribution data (default: 2012)"
        )
        parser.add_argument(
            "--region_type",
            type=str,
            choices=["pd", "district", "province", "gnd", "lg", "country", "moh", "ed", "dsd"],
            required=True,
            help="Type of regions to process (e.g., 'state', 'county')"
        )

    def handle(self, *args, **options):
        file_path = options["file_path"]
        year = options["year"]
        region_type = options["region_type"]

        # Define the expected age group columns
        age_group_columns = [
            'less_than_10', '10_~_19', '20_~_29', '30_~_39', 
            '40_~_49', '50_~_59', '60_~_69', '70_~_79', 
            '80_~_89', '90_and_above'
        ]

        try:
            # Use sep='\t' for TSV files
            data = pd.read_csv(file_path, sep='\t')
            total_rows = len(data)

            # Validate required columns exist
            required_columns = ['entity_id'] + age_group_columns
            missing_columns = [col for col in required_columns if col not in data.columns]
            if missing_columns:
                raise KeyError(f"Missing columns: {', '.join(missing_columns)}")

            # Get existing region IDs for the specified region type
            existing_region_ids = set(
                Region.objects.filter(type=region_type)
                .values_list('entity_id', flat=True)
            )
            
            self.stdout.write(
                f"Found {len(existing_region_ids)} existing {region_type} regions in database"
            )
            self.stdout.write(f"Starting import for {total_rows} age distribution records for year {year}...")

            # Statistics for reporting
            processed_count = 0
            skipped_count = 0
            invalid_count = 0

            # Use transaction to ensure data consistency
            with transaction.atomic():
                # Create progress bar
                for index, row in tqdm(data.iterrows(), total=total_rows, desc="Importing age distribution data"):
                    entity_id = row["entity_id"]
                    total_population = row["total_population"]
                    
                    # Skip if region doesn't exist
                    if entity_id not in existing_region_ids:
                        skipped_count += 1
                        continue

                    try:
                        # Get the region
                        region = Region.objects.get(entity_id=entity_id)

                        # Convert age group values to integers and validate
                        age_groups = {}
                        for column in age_group_columns:
                            try:
                                value = pd.to_numeric(str(row[column]).replace(",", ""), errors="coerce")
                                if pd.isna(value):
                                    raise ValueError(f"Invalid value for {column}")
                                age_groups[column] = int(value)
                            except (ValueError, TypeError):
                                raise ValueError(f"Invalid value for {column}")

                        ## Create or update age distribution
                        AgeDistribution.objects.update_or_create(
                            region=region,
                            year=year,
                            total_population=total_population,
                            less_than_10=age_groups["less_than_10"],    
                            age_10_to_19=age_groups["10_~_19"],
                            age_20_to_29=age_groups["20_~_29"],
                            age_30_to_39=age_groups["30_~_39"],
                            age_40_to_49=age_groups["40_~_49"],
                            age_50_to_59=age_groups["50_~_59"],
                            age_60_to_69=age_groups["60_~_69"],
                            age_70_to_79=age_groups["70_~_79"],
                            age_80_to_89=age_groups["80_~_89"],
                            age_90_and_above=age_groups["90_and_above"],
                        )

                        processed_count += 1

                    except ValueError as e:
                        invalid_count += 1
                        self.stdout.write(
                            self.style.WARNING(f"\nSkipping {entity_id}: {str(e)}")
                        )
                        continue
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"\nError processing {entity_id}: {str(e)}")
                        )
                        continue

            # Final report
            self.stdout.write("\nImport Summary:")
            self.stdout.write(f"Total records in file: {total_rows}")
            self.stdout.write(f"Successfully processed: {processed_count}")
            self.stdout.write(f"Skipped (no matching region): {skipped_count}")
            self.stdout.write(f"Skipped (invalid data): {invalid_count}")
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nSuccessfully imported age distribution data for year {year}. "
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
