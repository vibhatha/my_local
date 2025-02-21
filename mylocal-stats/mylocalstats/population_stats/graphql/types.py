from graphene_django import DjangoObjectType
from ..models import (
    Region,
    TotalPopulation,
    AgeDistribution,
    EthnicityDistribution,
    GenderDistribution,
    MaritalStatus,
    ReligiousAffiliation
)

class RegionType(DjangoObjectType):
    class Meta:
        model = Region
        fields = "__all__"

class TotalPopulationType(DjangoObjectType):
    class Meta:
        model = TotalPopulation
        fields = "__all__"

class AgeDistributionType(DjangoObjectType):
    class Meta:
        model = AgeDistribution
        fields = "__all__"

class EthnicityDistributionType(DjangoObjectType):
    class Meta:
        model = EthnicityDistribution
        fields = "__all__"

class GenderDistributionType(DjangoObjectType):
    class Meta:
        model = GenderDistribution
        fields = "__all__"

class MaritalStatusType(DjangoObjectType):
    class Meta:
        model = MaritalStatus
        fields = "__all__"

class ReligiousAffiliationType(DjangoObjectType):
    class Meta:
        model = ReligiousAffiliation
        fields = "__all__" 