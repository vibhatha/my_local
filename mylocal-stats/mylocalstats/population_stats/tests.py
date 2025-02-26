from django.test import TestCase
import pandas as pd
import json
import ast
from django.conf import settings
import os
from mylocalstats.population_stats.models import Region
from django.test.utils import override_settings
from django.db import connections


@override_settings(DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mylocal_test_db',
        'USER': settings.DATABASES['default']['USER'],
        'PASSWORD': settings.DATABASES['default']['PASSWORD'],
        'HOST': settings.DATABASES['default']['HOST'],
        'PORT': settings.DATABASES['default']['PORT'],
    }
})
class RegionDataImportTest(TestCase):
    """Test cases to verify TSV data is correctly imported into the database"""

    def setUp(self):
        """Set up test data paths and load sample data"""
        self.data_dir = os.path.join(settings.BASE_DIR, 'data')
        self.country_file = os.path.join(self.data_dir, 'country.tsv')
        self.province_file = os.path.join(self.data_dir, 'province.tsv')

        # Load sample data (10 records each)
        self.country_data = pd.read_csv(self.country_file, sep='\t').head(10)
        self.province_data = pd.read_csv(self.province_file, sep='\t').head(10)

        # Insert sample data into database
        for _, row in self.country_data.iterrows():
            self.create_region_from_row(row)
        
        for _, row in self.province_data.iterrows():
            self.create_region_from_row(row)

    def create_region_from_row(self, row):
        """Create a Region object from a TSV row"""
        # Handle centroid conversion
        centroid = None
        if pd.notna(row.get('centroid')):
            try:
                centroid = ast.literal_eval(row['centroid'])
            except (ValueError, SyntaxError):
                centroid = None

        # Create Region object
        region = Region(
            region_id=row['region_id'],
            name=row['name'],
            region_type=row['region_type'],
            parent_region_id=row['parent_region_id'] if pd.notna(row['parent_region_id']) else None,
            code=row['code'] if pd.notna(row['code']) else None,
            hasc=row['hasc'] if pd.notna(row['hasc']) else None,
            fips=row['fips'] if pd.notna(row['fips']) else None,
            latitude=float(centroid[0]) if centroid else None,
            longitude=float(centroid[1]) if centroid else None,
            centroid_altitude=float(row['centroid_altitude']) if pd.notna(row['centroid_altitude']) else None,
            population=int(row['population']) if pd.notna(row['population']) else None,
            area_sq_km=float(row['area_sq_km']) if pd.notna(row['area_sq_km']) else None,
            subs=row['subs'] if pd.notna(row['subs']) else None,
            supers=row['supers'] if pd.notna(row['supers']) else None,
            eqs=row['eqs'] if pd.notna(row['eqs']) else None,
            ints=row['ints'] if pd.notna(row['ints']) else None
        )
        region.save()

    def test_sample_data_import(self):
        """Test if sample data (10 records each) is correctly imported"""
        # Test countries
        db_countries = Region.objects.filter(region_type='Country')
        self.assertEqual(
            len(db_countries),
            len(self.country_data),
            f"Expected {len(self.country_data)} countries, found {len(db_countries)}"
        )

        # Test provinces
        db_provinces = Region.objects.filter(region_type='Province')
        self.assertEqual(
            len(db_provinces),
            len(self.province_data),
            f"Expected {len(self.province_data)} provinces, found {len(db_provinces)}"
        )

        # Test data integrity for countries
        for _, row in self.country_data.iterrows():
            record = Region.objects.get(region_id=row['region_id'])
            differences = self.compare_record_with_row(record, row)
            self.assertEqual(
                len(differences), 
                0, 
                f"Mismatches found for country {row['name']} ({row['region_id']}):\n" + 
                "\n".join(differences)
            )

        # Test data integrity for provinces
        for _, row in self.province_data.iterrows():
            record = Region.objects.get(region_id=row['region_id'])
            differences = self.compare_record_with_row(record, row)
            self.assertEqual(
                len(differences), 
                0, 
                f"Mismatches found for province {row['name']} ({row['region_id']}):\n" + 
                "\n".join(differences)
            )

    def test_sample_relationships(self):
        """Test relationships in sample data"""
        # Test province-country relationships
        for _, row in self.province_data.iterrows():
            if pd.notna(row['parent_region_id']):
                province = Region.objects.get(region_id=row['region_id'])
                self.assertTrue(
                    Region.objects.filter(region_id=province.parent_region_id).exists(),
                    f"Parent country not found for province {province.name} ({province.region_id})"
                )

    def compare_record_with_row(self, record, row):
        """Compare database record with TSV row and return list of differences"""
        differences = []
        
        # First check region_id as it's the primary key
        if record.region_id != row['region_id']:
            differences.append(f"region_id mismatch: DB={record.region_id}, TSV={row['region_id']}")
        
        # Extract coordinates from centroid
        if pd.notna(row.get('centroid')):
            try:
                centroid = ast.literal_eval(row['centroid'])
                if record.latitude != float(centroid[0]):
                    differences.append(f"Latitude mismatch: DB={record.latitude}, TSV={centroid[0]}")
                if record.longitude != float(centroid[1]):
                    differences.append(f"Longitude mismatch: DB={record.longitude}, TSV={centroid[1]}")
            except (ValueError, SyntaxError, IndexError) as e:
                differences.append(f"Centroid parsing error: {e}")

        # Compare basic fields
        basic_fields = {
            'name': str,
            'region_type': str,
            'parent_region_id': str,
            'code': str,
            'hasc': str,
            'fips': str,
            'centroid_altitude': float,
            'population': int,
            'area_sq_km': float,
        }

        for field, field_type in basic_fields.items():
            db_value = getattr(record, field)
            tsv_value = row.get(field)
            
            # Handle null values
            if pd.isna(tsv_value):
                if db_value is not None:
                    differences.append(f"{field} mismatch: DB={db_value}, TSV=None")
                continue
            
            # Convert and compare values
            try:
                tsv_value = field_type(tsv_value)
                if db_value != tsv_value:
                    differences.append(f"{field} mismatch: DB={db_value}, TSV={tsv_value}")
            except (ValueError, TypeError) as e:
                differences.append(f"{field} conversion error: {e}")

        # Compare JSON fields
        json_fields = ['subs', 'supers', 'eqs', 'ints']
        for field in json_fields:
            db_value = getattr(record, field)
            tsv_value = row.get(field)
            
            if pd.isna(tsv_value):
                if db_value is not None:
                    differences.append(f"{field} mismatch: DB={db_value}, TSV=None")
                continue
            
            try:
                db_json = json.loads(db_value) if db_value else None
                tsv_json = ast.literal_eval(tsv_value) if tsv_value else None
                if db_json != tsv_json:
                    differences.append(f"{field} mismatch: DB={db_json}, TSV={tsv_json}")
            except (json.JSONDecodeError, ValueError, SyntaxError) as e:
                differences.append(f"{field} parsing error: {e}")

        return differences

    def test_data_integrity(self):
        """Test data integrity constraints"""
        # Test that all parent_region_ids exist
        provinces = Region.objects.filter(region_type='Province')
        for province in provinces:
            if province.parent_region_id:
                self.assertTrue(
                    Region.objects.filter(region_id=province.parent_region_id).exists(),
                    f"Parent region {province.parent_region_id} not found for province {province.region_id}"
                )
        
        # Test that country codes are unique
        country_codes = Region.objects.filter(region_type='Country').values_list('code', flat=True)
        self.assertEqual(
            len(country_codes),
            len(set(country_codes)),
            "Duplicate country codes found"
        )

    def test_country_data_import(self):
        """Test if country TSV data matches database records"""
        # Read country TSV
        country_data = pd.read_csv(self.country_file, sep='\t')
        
        # Check if all records are imported
        db_count = Region.objects.filter(region_type='Country').count()
        self.assertEqual(
            db_count,
            len(country_data),
            f"Number of country records in database ({db_count}) doesn't match TSV ({len(country_data)})"
        )

        # Compare each record
        mismatches = []
        for _, row in country_data.iterrows():
            try:
                record = Region.objects.get(region_id=row['region_id'])
                differences = self.compare_record_with_row(record, row)
                if differences:
                    # Add sample data for debugging
                    mismatches.append(
                        f"Mismatches for {row['region_id']} (name: {row['name']}):\n" +
                        "\n".join(differences) +
                        f"\nTSV row: {row.to_dict()}\n" +
                        f"DB record: {record.__dict__}"
                    )
            except Region.DoesNotExist:
                mismatches.append(f"Record missing in DB for region_id: {row['region_id']} (name: {row['name']})")

        self.assertEqual(len(mismatches), 0, "\n\n".join(mismatches))

    def test_province_data_import(self):
        """Test if province TSV data matches database records"""
        # Read province TSV
        province_data = pd.read_csv(self.province_file, sep='\t')
        
        # Check if all records are imported
        self.assertEqual(
            Region.objects.filter(region_type='Province').count(),
            len(province_data),
            "Number of province records in database doesn't match TSV"
        )

        # Compare each record
        mismatches = []
        for _, row in province_data.iterrows():
            try:
                record = Region.objects.get(region_id=row['region_id'])
                differences = self.compare_record_with_row(record, row)
                if differences:
                    mismatches.append(f"Mismatches for {row['region_id']}:\n" + "\n".join(differences))
            except Region.DoesNotExist:
                mismatches.append(f"Record missing in DB for region_id: {row['region_id']}")

        self.assertEqual(len(mismatches), 0, "\n".join(mismatches))
