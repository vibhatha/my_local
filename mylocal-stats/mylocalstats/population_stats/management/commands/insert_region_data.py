import sys
import pandas as pd
from django.core.management.base import BaseCommand
from mylocalstats.population_stats.models import Region
from tqdm import tqdm


class Command(BaseCommand):
    """Insert region data from TSV file into the database.

    This command processes a TSV (Tab-Separated Values) file containing region data 
    and inserts it into the Region model. The TSV should have columns for region 
    ID and name. Region type is provided via command line argument.

    Examples:
        Insert province data:
            >>> python manage.py insert_region_data /path/to/regions.tsv --type province

    TSV Format Expected:
        id      name                type
        EC-01   Western Province    PD
        EC-02   Central Province    PD
        ...

    Args:
        file_path (str): Path to the TSV file containing the region data
        --type (str): Type of regions being inserted (province/district/city)

    Returns:
        None. Prints success message with number of records inserted.

    Raises:
        FileNotFoundError: If the specified TSV file doesn't exist
        ValueError: If the TSV format is invalid or required columns are missing
    """

    help = "Insert region data from TSV"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to the TSV file")
        parser.add_argument(
            "--type",
            type=str,
            choices=["PD", "District", "Province", "GND", "LG", "Country", "MOH", "ED", "DSD"],
            required=True,
            help="Type of regions being inserted (province/district/city)"
        )

    def handle(self, *args, **options):
        file_path = options["file_path"]
        region_type = options["type"].lower()

        try:
            # Use sep='\t' for TSV files
            data = pd.read_csv(file_path, sep='\t')
            total_rows = len(data)

            self.stdout.write(f"Starting import for {total_rows} {region_type}s...")

            # Create progress bar for regions
            for index, row in tqdm(data.iterrows(), total=total_rows, desc=f"Importing {region_type}s"):
                """
                Make sure the fields read are matching with the content in the files. 
                Or later make it generic so that the chosen fileds are passed as arguments.
                """
                entity_id = row["id"]
                region_name = row["name"]
                
                sys.stdout.write(f"\rProcessing {region_name} ({index + 1}/{total_rows})")
                sys.stdout.flush()

                # Create or update region
                Region.objects.update_or_create(
                    entity_id=entity_id,
                    defaults={
                        "name": region_name,
                        "type": region_type
                    }
                )

            # Add a newline at the end
            sys.stdout.write("\n")
            self.stdout.write(
                self.style.SUCCESS(f"Successfully imported data for {total_rows} {region_type}s")
            )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
        except pd.errors.EmptyDataError:
            self.stdout.write(self.style.ERROR("The TSV file is empty"))
        except KeyError as e:
            self.stdout.write(self.style.ERROR(f"Missing required column: {str(e)}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {str(e)}"))
