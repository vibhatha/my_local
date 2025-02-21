import graphene
from mylocalstats.population_stats.graphql.types import (
    RegionType,
    TotalPopulationType,
    AgeDistributionType,
    EthnicityDistributionType,
    GenderDistributionType,
    MaritalStatusType,
    ReligiousAffiliationType
)
from mylocalstats.population_stats.models import (
    Region,
    TotalPopulation,
    AgeDistribution,
    EthnicityDistribution,
    GenderDistribution,
    MaritalStatus,
    ReligiousAffiliation
)

class Query(graphene.ObjectType):
    # Region queries
    regions = graphene.List(
        RegionType,
        type=graphene.String(required=False)
    )
    region = graphene.Field(
        RegionType,
        entity_id=graphene.String(required=True)
    )

    # Total Population queries
    total_populations = graphene.List(
        TotalPopulationType,
        region_type=graphene.String(required=False),
        year=graphene.Int(required=False)
    )
    total_population = graphene.Field(
        TotalPopulationType,
        region_id=graphene.String(required=True)
    )

    # Age Distribution queries
    age_distributions = graphene.List(
        AgeDistributionType,
        region_type=graphene.String(required=False),
        year=graphene.Int(required=False)
    )
    age_distribution = graphene.Field(
        AgeDistributionType,
        region_id=graphene.String(required=True)
    )

    # Ethnicity Distribution queries
    ethnicity_distributions = graphene.List(
        EthnicityDistributionType,
        region_type=graphene.String(required=False),
        year=graphene.Int(required=False)
    )
    ethnicity_distribution = graphene.Field(
        EthnicityDistributionType,
        region_id=graphene.String(required=True)
    )

    # Gender Distribution queries
    gender_distributions = graphene.List(
        GenderDistributionType,
        region_type=graphene.String(required=False),
        year=graphene.Int(required=False)
    )
    gender_distribution = graphene.Field(
        GenderDistributionType,
        region_id=graphene.String(required=True)
    )

    # Marital Status queries
    marital_statuses = graphene.List(
        MaritalStatusType,
        region_type=graphene.String(required=False),
        year=graphene.Int(required=False)
    )
    marital_status = graphene.Field(
        MaritalStatusType,
        region_id=graphene.String(required=True)
    )

    # Religious Affiliation queries
    religious_affiliations = graphene.List(
        ReligiousAffiliationType,
        region_type=graphene.String(required=False),
        year=graphene.Int(required=False)
    )
    religious_affiliation = graphene.Field(
        ReligiousAffiliationType,
        region_id=graphene.String(required=True)
    )

    # Region resolvers
    def resolve_regions(self, info, type=None):
        queryset = Region.objects.all()
        if type:
            queryset = queryset.filter(type__iexact=type)
        return queryset

    def resolve_region(self, info, entity_id):
        return Region.objects.get(entity_id=entity_id)

    # Total Population resolvers
    def resolve_total_populations(self, info, region_type=None, year=None):
        queryset = TotalPopulation.objects.all()
        if region_type:
            queryset = queryset.filter(region__type__iexact=region_type)
        if year:
            queryset = queryset.filter(year=year)
        return queryset

    def resolve_total_population(self, info, region_id):
        return TotalPopulation.objects.get(region__entity_id=region_id)

    # Age Distribution resolvers
    def resolve_age_distributions(self, info, region_type=None, year=None):
        queryset = AgeDistribution.objects.all()
        if region_type:
            queryset = queryset.filter(region__type__iexact=region_type)
        if year:
            queryset = queryset.filter(year=year)
        return queryset

    def resolve_age_distribution(self, info, region_id):
        return AgeDistribution.objects.get(region__entity_id=region_id)

    # Ethnicity Distribution resolvers
    def resolve_ethnicity_distributions(self, info, region_type=None, year=None):
        queryset = EthnicityDistribution.objects.all()
        if region_type:
            queryset = queryset.filter(region__type__iexact=region_type)
        if year:
            queryset = queryset.filter(year=year)
        return queryset

    def resolve_ethnicity_distribution(self, info, region_id):
        return EthnicityDistribution.objects.get(region__entity_id=region_id)

    # Gender Distribution resolvers
    def resolve_gender_distributions(self, info, region_type=None, year=None):
        queryset = GenderDistribution.objects.all()
        if region_type:
            queryset = queryset.filter(region__type__iexact=region_type)
        if year:
            queryset = queryset.filter(year=year)
        return queryset

    def resolve_gender_distribution(self, info, region_id):
        return GenderDistribution.objects.get(region__entity_id=region_id)

    # Marital Status resolvers
    def resolve_marital_statuses(self, info, region_type=None, year=None):
        queryset = MaritalStatus.objects.all()
        if region_type:
            queryset = queryset.filter(region__type__iexact=region_type)
        if year:
            queryset = queryset.filter(year=year)
        return queryset

    def resolve_marital_status(self, info, region_id):
        return MaritalStatus.objects.get(region__entity_id=region_id)

    # Religious Affiliation resolvers
    def resolve_religious_affiliations(self, info, region_type=None, year=None):
        queryset = ReligiousAffiliation.objects.all()
        if region_type:
            queryset = queryset.filter(region__type__iexact=region_type)
        if year:
            queryset = queryset.filter(year=year)
        return queryset

    def resolve_religious_affiliation(self, info, region_id):
        return ReligiousAffiliation.objects.get(region__entity_id=region_id) 