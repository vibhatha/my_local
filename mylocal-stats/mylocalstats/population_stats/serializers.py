from rest_framework import serializers
from mylocalstats.population_stats.models import Region, TotalPopulation

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'

class TotalPopulationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TotalPopulation
        fields = '__all__' 