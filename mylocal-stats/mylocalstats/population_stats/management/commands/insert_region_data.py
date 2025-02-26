import sys
import json
import pandas as pd
import ast  # For safely evaluating string representations of arrays
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
        region_id    name    region_type  parent_region_id  code    latitude    longitude   centroid_altitude   population  area_sq_km   subs    supers  eqs     ints    other_ids   etc...
        EC-01       Name1   Province     null              CODE1   6.927079    79.861243   45.5                1000000     234.5       []      []      []      []      {}          ...

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
            help="Type of regions being inserted"
        )

    def collect_other_ids(self, row):
        """Collect all columns ending with '_id' into a dictionary, excluding region_id and parent_region_id"""
        other_ids = {}
        excluded_ids = {'region_id', 'parent_region_id'}
        
        for column in row.index:
            if column.endswith('_id') and column not in excluded_ids:
                if pd.notna(row[column]):  # Only include non-null values
                    # Strip the '_id' suffix to use as the key
                    key = column[:-3]  # remove '_id' from the end
                    other_ids[key] = row[column]
        
        return other_ids

    def extract_coordinates(self, centroid_str):
        """Extract latitude and longitude from centroid string"""
        if pd.isna(centroid_str):
            return None, None
        
        try:
            # Convert string representation of array to actual array
            centroid = ast.literal_eval(centroid_str)
            if isinstance(centroid, (list, tuple)) and len(centroid) >= 2:
                # Round to 6 decimal places to match model's DecimalField precision
                latitude = round(float(centroid[0]), 6)
                longitude = round(float(centroid[1]), 6)
                return latitude, longitude
        except (ValueError, SyntaxError, IndexError) as e:
            self.stdout.write(
                self.style.WARNING(
                    f"Error parsing centroid coordinates: {centroid_str}, Error: {str(e)}"
                )
            )
        
        return None, None

    def handle(self, *args, **options):
        file_path = options["file_path"]
        region_type = options["type"]

        try:
            # Use sep='\t' for TSV files
            data = pd.read_csv(file_path, sep='\t')
            total_rows = len(data)

            self.stdout.write(f"Starting import for {total_rows} {region_type}s...")
            
            # Keep track of processed records
            processed_count = 0
            updated_count = 0
            created_count = 0

            # Create progress bar for regions
            for index, row in tqdm(data.iterrows(), total=total_rows, desc=f"Importing {region_type}s"):
                try:
                    # Get region_id or use 'N/A' if not available
                    region_id = row.get("id", "N/A")
                    if pd.isna(region_id):
                        region_id = f"N/A_{region_type}_{index}"  # Make unique N/A IDs
                    
                    # Debug print
                    self.stdout.write(f"Processing region_id: {region_id}")
                    
                    # Extract latitude and longitude from centroid
                    latitude, longitude = self.extract_coordinates(row.get("centroid"))
                    
                    # Collect all *_id fields into other_ids
                    other_ids = self.collect_other_ids(row)
                    
                    # Convert JSON strings to proper format if they exist
                    subs = json.dumps(row.get("subs", [])) if pd.notna(row.get("subs")) else None
                    supers = json.dumps(row.get("supers", [])) if pd.notna(row.get("supers")) else None
                    eqs = json.dumps(row.get("eqs", [])) if pd.notna(row.get("eqs")) else None
                    ints = json.dumps(row.get("ints", [])) if pd.notna(row.get("ints")) else None
                    other_ids_json = json.dumps(other_ids) if other_ids else None

                    # Create or update region
                    obj, created = Region.objects.update_or_create(
                        region_id=region_id,
                        defaults={
                            "name": row.get("name", f"Unknown_{region_type}_{index}"),
                            "region_type": region_type,
                            "parent_region_id": row.get("parent_region_id") if pd.notna(row.get("parent_region_id")) else None,
                            "code": row.get("code") if pd.notna(row.get("code")) else None,
                            "hasc": row.get("hasc") if pd.notna(row.get("hasc")) else None,
                            "fips": row.get("fips") if pd.notna(row.get("fips")) else None,
                            "latitude": latitude,
                            "longitude": longitude,
                            "centroid_altitude": row.get("centroid_altitude") if pd.notna(row.get("centroid_altitude")) else None,
                            "population": row.get("population") if pd.notna(row.get("population")) else None,
                            "area_sq_km": row.get("area") if pd.notna(row.get("area")) else None,
                            "subs": subs,
                            "supers": supers,
                            "eqs": eqs,
                            "ints": ints,
                            "other_ids": other_ids_json
                        }
                    )

                    processed_count += 1
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

                except Exception as row_error:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Error processing row {index + 1}: {str(row_error)}"
                        )
                    )
                    continue

            self.stdout.write(
                self.style.SUCCESS(
                    f"Import completed:\n"
                    f"Total processed: {processed_count}\n"
                    f"Created: {created_count}\n"
                    f"Updated: {updated_count}"
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
