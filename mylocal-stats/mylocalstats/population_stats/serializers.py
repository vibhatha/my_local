from rest_framework import serializers
from mylocalstats.population_stats.models import Region, TotalPopulation
from mylocalstats.population_stats.models import AgeDistribution
from mylocalstats.population_stats.models import EthnicityDistribution
from mylocalstats.population_stats.models import GenderDistribution
from mylocalstats.population_stats.models import MaritalStatus
from mylocalstats.population_stats.models import ReligiousAffiliation

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'

class TotalPopulationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TotalPopulation
        fields = '__all__'

class AgeDistributionSerializer(serializers.ModelSerializer):
    region_id = serializers.CharField(source='region.entity_id')
    region_name = serializers.CharField(source='region.name')
    
    class Meta:
        model = AgeDistribution
        fields = [
            'region_id',
            'region_name',
            'total_population',
            'less_than_10',
            'age_10_to_19',
            'age_20_to_29',
            'age_30_to_39',
            'age_40_to_49',
            'age_50_to_59',
            'age_60_to_69',
            'age_70_to_79',
            'age_80_to_89',
            'age_90_and_above',
            'year'
        ]

class EthnicityDistributionSerializer(serializers.ModelSerializer):
    region_id = serializers.CharField(source='region.entity_id')
    region_name = serializers.CharField(source='region.name')
    
    class Meta:
        model = EthnicityDistribution
        fields = [
            'region_id',
            'region_name',
            'total_population',
            'sinhalese',
            'sl_tamil',
            'ind_tamil',
            'sl_moor',
            'burgher',
            'malay',
            'sl_chetty',
            'bharatha',
            'other_eth',
            'year'
        ]

class GenderDistributionSerializer(serializers.ModelSerializer):
    region_id = serializers.CharField(source='region.entity_id')
    region_name = serializers.CharField(source='region.name')
    
    class Meta:
        model = GenderDistribution
        fields = [
            'region_id',
            'region_name',
            'year',
            'total_population',
            'male',
            'female'
        ]

class MaritalStatusSerializer(serializers.ModelSerializer):
    region_id = serializers.CharField(source='region.entity_id')
    region_name = serializers.CharField(source='region.name')
    
    class Meta:
        model = MaritalStatus
        fields = [
            'region_id',
            'region_name',
            'year',
            'total_population',
            'never_married',
            'married_registered',
            'married_customary',
            'separated_legally',
            'separated_non_legal',
            'divorced', 'widowed', 'not_stated'
        ]

class ReligiousAffiliationSerializer(serializers.ModelSerializer):
    """Serializer for religious affiliation data.
    
    Converts ReligiousAffiliation model instances to/from JSON format.
    """
    region_id = serializers.CharField(source='region.entity_id')
    region_name = serializers.CharField(source='region.name')
    
    class Meta:
        model = ReligiousAffiliation
        fields = [
            'region_id',
            'region_name',
            'year',
            'total_population',
            'buddhist',
            'hindu',
            'islam',
            'roman_catholic',
            'other_christian',
            'other'
        ] 