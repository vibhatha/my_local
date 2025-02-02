import pytest
from django.test import TestCase
from mylocalstats.population_stats.models import Region

class TestRegion(TestCase):
    def test_region_creation(self):
        region = Region.objects.create(
            entity_id="TEST001",
            name="Test Region"
        )
        self.assertEqual(region.name, "Test Region")