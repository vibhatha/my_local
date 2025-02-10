from django.core.management.base import BaseCommand
from django.db import transaction
from mylocalstats.population_stats.models import Region, EthnicityDistribution
import csv
from tqdm import tqdm
import sys

class Command(BaseCommand):
    """Insert ethnicity distribution data from TSV file into the database.

    This command processes a TSV file containing ethnicity distribution data and links it
    to existing regions in the database. Only processes records where the entity_id
    matches an existing region of the specified type.

    Examples:
        Insert ethnicity data for MOH regions in 2012:
            >>> python manage.py insert_ethnicity_distribution /path/to/file.tsv --year 2012 --region-type MOH
        
        Insert ethnicity data for EC regions in 2012:
            >>> python manage.py insert_ethnicity_distribution /path/to/file.tsv --year 2012 --region-type EC
    """

    help = 'Insert ethnicity distribution data from TSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the TSV file')
        parser.add_argument(
            '--year',
            type=int,
            default=2012,
            help='Year of the data (default: 2012)'
        )
        parser.add_argument(
            '--region-type',
            type=str,
            choices=['pd', 'district', 'province', 'gnd', 'lg', 'country', 'moh', 'ed', 'dsd', 'ec'],
            required=True,
            help='Type of region (e.g., MOH, EC)'
        )

    def validate_numeric(self, value, field_name, entity_id):
        """Validate and convert numeric values"""
        try:
            value = float(value)
            if value < 0:
                raise ValueError(f"Negative value not allowed for {field_name}")
            return value
        except ValueError as e:
            raise ValueError(f"Invalid {field_name} value for region {entity_id}: {str(e)}")

    def validate_row(self, row, entity_id):
        """Validate all fields in a row"""
        required_fields = [
            'total_population', 'sinhalese', 'sl_tamil', 'ind_tamil',
            'sl_moor', 'burgher', 'malay', 'sl_chetty', 'bharatha', 'other_eth'
        ]
        
        validated_data = {}
        
        # Check for missing fields
        missing_fields = [field for field in required_fields if field not in row]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
            
        # Validate each numeric field
        for field in required_fields:
            validated_data[field] = self.validate_numeric(row[field], field, entity_id)
            
        # Validate total population matches sum of ethnicities
        total = validated_data['total_population']
        sum_ethnicities = sum(validated_data[field] for field in required_fields[1:])
        
        # Allow for small floating point differences (0.1%)
        if abs(total - sum_ethnicities) > (total * 0.001):
            raise ValueError(
                f"Total population ({total}) does not match sum of ethnicities ({sum_ethnicities})"
            )
            
        return validated_data

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        year = kwargs['year']
        region_type = kwargs['region_type'].lower()  # Convert to lowercase for consistency
        success_count = 0
        error_count = 0
        skipped_count = 0
        
        try:
            # First, get all existing region IDs for the specified type
            existing_regions = set(
                Region.objects.filter(
                    type=region_type
                ).values_list('entity_id', flat=True)
            )
            
            if not existing_regions:
                self.stdout.write(
                    self.style.ERROR(f"No regions found for type: {region_type}")
                )
                return
                
            self.stdout.write(
                self.style.SUCCESS(f"Found {len(existing_regions)} existing {region_type} regions in database")
            )
            
            # Read file first to get total count for progress bar
            with open(file_path, 'r') as file:
                total_rows = sum(1 for _ in file) - 1  # Subtract 1 for header
            
            self.stdout.write(f"Starting import for {total_rows} ethnicity distribution records for year {year}...")
            
            with open(file_path, 'r') as file:
                tsv_reader = csv.DictReader(file, delimiter='\t')
                
                # Use transaction to ensure data consistency
                with transaction.atomic():
                    for row in tqdm(tsv_reader, total=total_rows, desc=f"Processing {region_type} ethnicity data"):
                        try:
                            entity_id = row['entity_id'].strip()
                            
                            # Skip empty rows
                            if not entity_id:
                                skipped_count += 1
                                continue
                                
                            # Skip if region doesn't exist or doesn't match type
                            if entity_id not in existing_regions:
                                skipped_count += 1
                                continue
                            
                            # Validate all data before processing
                            try:
                                validated_data = self.validate_row(row, entity_id)
                            except ValueError as e:
                                self.stdout.write(
                                    self.style.WARNING(f"\nSkipping {entity_id}: {str(e)}")
                                )
                                error_count += 1
                                continue
                            
                            region = Region.objects.get(entity_id=entity_id)
                            
                            # Create or update ethnicity distribution
                            ethnicity_dist, created = EthnicityDistribution.objects.update_or_create(
                                region=region,
                                year=year,
                                total_population=validated_data['total_population'],
                                sinhalese=validated_data['sinhalese'],
                                sl_tamil=validated_data['sl_tamil'],
                                ind_tamil=validated_data['ind_tamil'],
                                sl_moor=validated_data['sl_moor'],
                                burgher=validated_data['burgher'],
                                malay=validated_data['malay'],
                                sl_chetty=validated_data['sl_chetty'],
                                bharatha=validated_data['bharatha'],
                                other_eth=validated_data['other_eth']
                            )
                            
                            if created:
                                success_count += 1
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f'\rSuccessfully inserted ethnicity data for region {entity_id}'
                                    )
                                )
                                sys.stdout.flush()
                            else:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'\rUpdated existing ethnicity data for region {entity_id}'
                                    )
                                )
                                sys.stdout.flush()

                        except Exception as e:
                            error_count += 1
                            self.stdout.write(
                                self.style.ERROR(f"\nError processing {entity_id}: {str(e)}")
                            )
                            continue

            # Final report
            self.stdout.write("\nImport Summary:")
            self.stdout.write(f"Total records in file: {total_rows}")
            self.stdout.write(f"Successfully processed: {success_count}")
            self.stdout.write(f"Skipped (no matching region): {skipped_count}")
            self.stdout.write(f"Skipped (invalid data): {error_count}")
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nSuccessfully imported ethnicity distribution data for year {year}. "
                    f"Processed {success_count} out of {total_rows} records."
                )
            )
                    
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to process file: {str(e)}")
            )