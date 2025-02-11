import sys
import pandas as pd
from django.core.management.base import BaseCommand
from mylocalstats.population_stats.models import Region, GenderDistribution
from tqdm import tqdm


class Command(BaseCommand):
    """Insert gender distribution data from TSV file into the database.

    This command processes a TSV file containing gender distribution data
    and inserts it into the GenderDistribution model. The TSV should have columns for
    region ID, total population, male and female counts.

    Examples:
        Insert gender distribution data:
            >>> python manage.py insert_gender_distribution /path/to/population-gender.regions.2012.tsv --type PD

    TSV Format Expected:
        entity_id    total_population    male    female
        EC-01       2324349.0           1140472.0    1183877.0
        EC-02       2304833.0           1116893.0    1187940.0
        ...

    Args:
        file_path (str): Path to the TSV file containing the gender distribution data
        entity_file (str): Path to the TSV file containing region entities
        --type (str): Type of regions to process (e.g., PD, District, Province)
        --year (int): Year of the data (default: 2012)

    Returns:
        None. Prints success message with number of records processed.
    """

    help = "Insert gender distribution data from TSV file"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to the TSV file containing gender distribution data")
        parser.add_argument("region_file", type=str, help="Path to the TSV file containing region entities")
        parser.add_argument(
            "--type",
            type=str,
            choices=["pd", "district", "province", "gnd", "lg", "country", "moh", "ed", "dsd"],
            required=True,
            help="Type of regions to process"
        )
        parser.add_argument(
            "--year",
            type=int,
            default=2012,
            help="Year of the data (default: 2012)"
        )

    def handle(self, *args, **options):
        file_path = options["file_path"]
        region_file = options["region_file"]
        region_type = options["type"]
        year = options["year"]
        
        try:
            # Read the entity file from the provided path
            entities_df = pd.read_csv(region_file, sep='\t')
            
            # Read the population-gender data
            gender_df = pd.read_csv(file_path, sep='\t')
            
            # Merge the dataframes to get only relevant records
            merged_df = pd.merge(
                gender_df,
                entities_df[['id', 'name']],
                left_on='entity_id',
                right_on='id',
                how='inner'
            )

            print(merged_df.head())
            
            self.stdout.write(f"Found {len(merged_df)} matching records to process...")
            
            success_count = 0
            for _, row in tqdm(merged_df.iterrows(), total=len(merged_df)):
                try:
                    region = Region.objects.get(entity_id=row['entity_id'], type=region_type)
                    
                    print_region(region=region)
                    
                    # Validate the data
                    total_pop = int(row['total_population'])
                    male_pop = int(row['male'])
                    female_pop = int(row['female'])
                    
                    if total_pop != (male_pop + female_pop):
                        self.stdout.write(f'\rWarning: {row["entity_id"]} - Population mismatch')
                        continue
                    
                    # Create or update gender distribution
                    gender_dist, created = GenderDistribution.objects.update_or_create(
                        region=region,
                        year=year,
                        defaults={
                            'total_population': total_pop,
                            'male': male_pop,
                            'female': female_pop,
                        }
                    )
                    
                    if created:
                        success_count += 1
                    
                except Region.DoesNotExist:
                    self.stdout.write(f'\rSkipping {row["entity_id"]}: Region not found')
                    continue
                except Exception as e:
                    self.stdout.write(f'\rError processing {row["entity_id"]}: {str(e)}')
                    continue
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully processed {success_count} new records out of {len(merged_df)} total records"
                )
            )
            
        except FileNotFoundError as e:
            self.stdout.write(self.style.ERROR(f"File not found: {str(e)}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {str(e)}"))


def print_region(region: Region):
    print(f"\rCurrently evaluating region: {region.entity_id} - {region.name}\n", end='', flush=True)
    sys.stdout.flush()