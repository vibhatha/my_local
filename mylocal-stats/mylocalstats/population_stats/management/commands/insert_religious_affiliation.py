import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from mylocalstats.population_stats.models import Region, ReligiousAffiliation
from tqdm import tqdm


class Command(BaseCommand):
    """Insert religious affiliation data from TSV files into the database.
    
    Reads religious affiliation statistics from a TSV file and creates corresponding
    ReligiousAffiliation records in the database. The data is matched with existing
    regions using a provided region mapping file.
    
    Example:
        python manage.py insert_religious_affiliation \\
            data/religious_stats.tsv \\
            data/region_mapping.tsv \\
            province
    """
    
    help = 'Insert religious affiliation data from TSV files'

    def add_arguments(self, parser):
        """Define command-line arguments for the command.
        
        Args:
            data_file (str): TSV file containing religious affiliation statistics
            region_file (str): TSV file containing region entity ID mappings
            region_type (str): Type of region to process (e.g., province, district)
            year (int): Year of the data (defaults to 2012)
        """
        parser.add_argument('data_file', type=str, help='Path to religious affiliation data file')
        parser.add_argument('region_file', type=str, help='Path to region mapping file')
        parser.add_argument('--year', type=int, default=2012)
        parser.add_argument(
            '--region_type',
            type=str,
            required=True,
            choices=['province', 'district', 'dsd', 'gnd', 'ed', 'lg', 'pd', 'moh', 'country']
        )

    def handle(self, *args, **kwargs):
        """Process and import religious affiliation data.
        
        Reads the input files, validates regions, and creates ReligiousAffiliation
        records in the database. Existing records for the specified region type
        are deleted before importing new data.
        
        Args:
            data_file (str): Path to religious affiliation data file
            region_file (str): Path to region mapping file
            region_type (str): Type of region to process
            
        Returns:
            None
            
        Raises:
            Exception: If there are any errors during file reading or data processing
        """
        try:
            # Load both TSV files
            data_df = pd.read_csv(kwargs['data_file'], sep='\t')
            region_df = pd.read_csv(kwargs['region_file'], sep='\t')
            
            # Merge dataframes on entity_id
            merged_df = pd.merge(
                data_df,
                region_df[['id', 'name']],
                left_on='entity_id',
                right_on='id',
                how='inner'
            )
            
            self.stdout.write(f"Found {len(merged_df)} matching records in files")
            
            # Get existing regions of the specified type
            existing_regions = {
                r.entity_id: r for r in Region.objects.filter(type=kwargs['region_type'].lower())
            }
            
            self.stdout.write(f"Found {len(existing_regions)} existing regions in database")
            
            processed = 0
            skipped = 0
            
            with transaction.atomic():
                # Delete existing records for the specified region type
                ReligiousAffiliation.objects.filter(
                    region__type__iexact=kwargs['region_type'],
                    year=kwargs['year']
                ).delete()
                
                # Process the merged data
                religious_affiliations = []
                for _, row in tqdm(merged_df.iterrows(), total=len(merged_df)):
                    entity_id = row['entity_id']
                    
                    # Skip if region doesn't exist in database
                    if entity_id not in existing_regions:
                        skipped += 1
                        continue
                    
                    religious_affiliations.append(
                        ReligiousAffiliation(
                            region=existing_regions[entity_id],
                            year=kwargs['year'],
                            total_population=row['total_population'],
                            buddhist=row['buddhist'],
                            hindu=row['hindu'],
                            islam=row['islam'],
                            roman_catholic=row['roman_catholic'],
                            other_christian=row['other_christian'],
                            other=row['other']
                        )
                    )
                    processed += 1
                
                # Bulk create all records at once
                ReligiousAffiliation.objects.bulk_create(religious_affiliations)
            
            # Final report
            self.stdout.write("\nImport Summary:")
            self.stdout.write(f"Total matching records in files: {len(merged_df)}")
            self.stdout.write(f"Successfully processed: {processed}")
            self.stdout.write(f"Skipped (region not in database): {skipped}")
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nSuccessfully imported religious affiliation data for {processed} regions"
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error: {str(e)}")
            )
