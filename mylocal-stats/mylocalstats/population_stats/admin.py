from django.contrib import admin
from .models import (
    Region,
    TotalPopulation,
    AgeDistribution,
    EthnicityDistribution,
    GenderDistribution,
    MaritalStatus,
    ReligiousAffiliation
)

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('region_id', 'name', 'region_type', 'code')
    list_filter = ('region_type',)
    search_fields = ('region_id', 'name', 'code')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(TotalPopulation)
class TotalPopulationAdmin(admin.ModelAdmin):
    list_display = ('region', 'total_population', 'year')
    search_fields = ('region__name',)

@admin.register(AgeDistribution)
class AgeDistributionAdmin(admin.ModelAdmin):
    list_display = ('region', 'total_population', 'year')
    search_fields = ('region__name',)

@admin.register(EthnicityDistribution)
class EthnicityDistributionAdmin(admin.ModelAdmin):
    list_display = ('region', 'total_population', 'year')
    search_fields = ('region__name',)

@admin.register(GenderDistribution)
class GenderDistributionAdmin(admin.ModelAdmin):
    list_display = ('region', 'total_population', 'male', 'female', 'year')
    search_fields = ('region__name',)

@admin.register(MaritalStatus)
class MaritalStatusAdmin(admin.ModelAdmin):
    list_display = ('region', 'total_population', 'year')
    search_fields = ('region__name',)

@admin.register(ReligiousAffiliation)
class ReligiousAffiliationAdmin(admin.ModelAdmin):
    list_display = ('region', 'total_population', 'year')
    search_fields = ('region__name',)