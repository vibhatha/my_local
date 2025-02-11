import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from mylocalstats.population_stats.models import Region, MaritalStatus
from tqdm import tqdm

class Command(BaseCommand):
    """Insert marital status distribution data from TSV files.
    
    Example:
        python manage.py insert_marital_status marital_status.tsv province.tsv --year 2012 --region_type province
    """
    
    def add_arguments(self, parser):
        parser.add_argument('data_file', type=str, help='Path to marital status data TSV file')
        parser.add_argument('region_file', type=str, help='Path to region TSV file')
        parser.add_argument('--year', type=int, default=2012)
        parser.add_argument(
            '--region_type',
            type=str,
            required=True,
            choices=['province', 'district', 'dsd', 'gnd', 'ed', 'lg', 'pd', 'moh', 'country']
        )

    def handle(self, *args, **options):
        try:
            # Load both TSV files
            data_df = pd.read_csv(options['data_file'], sep='\t')
            region_df = pd.read_csv(options['region_file'], sep='\t')
            
            # Merge dataframes on entity_id
            merged_df = pd.merge(
                data_df,
                region_df[['id', 'name']],  # We only need these columns
                left_on='entity_id',
                right_on='id',
                how='inner'
            )
            
            self.stdout.write(f"Found {len(merged_df)} matching records in files")
            
            # Get existing regions of the specified type
            existing_regions = {
                r.entity_id: r for r in Region.objects.filter(type=options['region_type'])
            }
            
            self.stdout.write(f"Found {len(existing_regions)} existing regions in database")
            
            # Statistics for reporting
            processed = 0
            skipped = 0
            
            # Process the merged data
            with transaction.atomic():
                for _, row in tqdm(merged_df.iterrows(), total=len(merged_df)):
                    entity_id = row['entity_id']
                    
                    # Skip if region doesn't exist in database
                    if entity_id not in existing_regions:
                        skipped += 1
                        continue
                    
                    region = existing_regions[entity_id]
                    
                    MaritalStatus.objects.update_or_create(
                        region=region,
                        year=options['year'],
                        defaults={
                            'total_population': row['total_population'],
                            'never_married': row['never_married'],
                            'married_registered': row['married_((registered)'],
                            'married_customary': row['married_(customary)'],
                            'separated_legally': row['legally_separated'],
                            'separated_non_legal': row['separated_(not_legally)'],
                            'divorced': row['divorced'],
                            'widowed': row['widowed'],
                            'not_stated': row['not_stated']
                        }
                    )
                    processed += 1
            
            # Final report
            self.stdout.write("\nImport Summary:")
            self.stdout.write(f"Total matching records in files: {len(merged_df)}")
            self.stdout.write(f"Successfully processed: {processed}")
            self.stdout.write(f"Skipped (region not in database): {skipped}")
            
            self.stdout.write(self.style.SUCCESS(
                f"\nSuccessfully imported marital status data for {processed} regions"
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
