from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from mylocalstats.population_stats.models import Region, TotalPopulation, AgeDistribution, EthnicityDistribution, GenderDistribution, MaritalStatus, ReligiousAffiliation
from mylocalstats.population_stats.serializers import (
    RegionSerializer, 
    TotalPopulationSerializer, 
    AgeDistributionSerializer, 
    EthnicityDistributionSerializer,
    GenderDistributionSerializer,
    MaritalStatusSerializer,
    ReligiousAffiliationSerializer
)
from rest_framework.reverse import reverse

@api_view(['GET'])
def get_regions_by_type(request, region_type):
    try:
        regions = Region.objects.filter(type__iexact=region_type)
        if not regions.exists():
            return Response(
                {"error": f"No regions found of type: {region_type}"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = RegionSerializer(regions, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
def get_region_by_id(request, region_id):
    try:
        region = Region.objects.get(entity_id=region_id)
        serializer = RegionSerializer(region)
        return Response(serializer.data)
    except Region.DoesNotExist:
        return Response(
            {"error": "Region not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
def get_population_by_region_type(request, region_type):
    try:
        regions = Region.objects.filter(type__iexact=region_type)
        if not regions.exists():
            return Response(
                {"error": f"No regions found of type: {region_type}"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        population = TotalPopulation.objects.filter(region__in=regions)
        serializer = TotalPopulationSerializer(population, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
def get_population_by_region_id(request, region_id):
    try:
        region = Region.objects.get(entity_id=region_id)
        population = TotalPopulation.objects.filter(region=region)
        serializer = TotalPopulationSerializer(population, many=True)
        return Response(serializer.data)
    except Region.DoesNotExist:
        return Response(
            {"error": "Region not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
def get_age_distribution_by_region_type(request, region_type):
    try:
        regions = Region.objects.filter(type__iexact=region_type)
        if not regions.exists():
            return Response(
                {"error": f"No regions found of type: {region_type}"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        age_distributions = AgeDistribution.objects.filter(region__in=regions)
        serializer = AgeDistributionSerializer(age_distributions, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
def get_age_distribution_by_region_id(request, region_id):
    try:
        region = Region.objects.get(entity_id=region_id)
        age_distribution = AgeDistribution.objects.get(region=region)
        serializer = AgeDistributionSerializer(age_distribution)
        return Response(serializer.data)
    except Region.DoesNotExist:
        return Response(
            {"error": "Region not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except AgeDistribution.DoesNotExist:
        return Response(
            {"error": "Age distribution data not found for this region"}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
def get_ethnicity_distribution_by_region_type(request, region_type):
    try:
        regions = Region.objects.filter(type__iexact=region_type)
        if not regions.exists():
            return Response(
                {"error": f"No regions found of type: {region_type}"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        ethnicity_distributions = EthnicityDistribution.objects.filter(region__in=regions)
        serializer = EthnicityDistributionSerializer(ethnicity_distributions, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
def get_ethnicity_distribution_by_region_id(request, region_id):
    try:
        region = Region.objects.get(entity_id=region_id)
        ethnicity_distribution = EthnicityDistribution.objects.get(region=region)
        serializer = EthnicityDistributionSerializer(ethnicity_distribution)
        return Response(serializer.data)
    except Region.DoesNotExist:
        return Response(
            {"error": "Region not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except EthnicityDistribution.DoesNotExist:
        return Response(
            {"error": "Ethnicity distribution data not found for this region"}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
def get_gender_distribution_by_region_type(request, region_type):
    try:
        regions = Region.objects.filter(type__iexact=region_type)
        if not regions.exists():
            return Response(
                {"error": f"No regions found of type: {region_type}"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        gender_distributions = GenderDistribution.objects.filter(region__in=regions)
        serializer = GenderDistributionSerializer(gender_distributions, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
def get_gender_distribution_by_region_id(request, region_id):
    try:
        region = Region.objects.get(entity_id=region_id)
        gender_distribution = GenderDistribution.objects.get(region=region)
        serializer = GenderDistributionSerializer(gender_distribution)
        return Response(serializer.data)
    except Region.DoesNotExist:
        return Response(
            {"error": "Region not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except GenderDistribution.DoesNotExist:
        return Response(
            {"error": "Gender distribution data not found for this region"}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
def get_marital_status_by_region_type(request, region_type):
    try:
        regions = Region.objects.filter(type__iexact=region_type)
        if not regions.exists():
            return Response(
                {"error": f"No regions found of type: {region_type}"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        marital_status = MaritalStatus.objects.filter(region__in=regions)
        serializer = MaritalStatusSerializer(marital_status, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
def get_marital_status_by_region_id(request, region_id):
    try:
        region = Region.objects.get(entity_id=region_id)
        marital_status = MaritalStatus.objects.get(region=region)
        serializer = MaritalStatusSerializer(marital_status)
        return Response(serializer.data)
    except Region.DoesNotExist:
        return Response(
            {"error": "Region not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except MaritalStatus.DoesNotExist:
        return Response(
            {"error": "Marital status data not found for this region"}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
def get_religious_affiliation_by_region_type(request, region_type):
    """Get religious affiliation data for all regions of a specific type.
    
    Args:
        request: HTTP request object
        region_type (str): Type of region (e.g., province, district)
        
    Returns:
        Response: JSON response containing religious affiliation data
    """
    try:
        regions = Region.objects.filter(type__iexact=region_type)
        if not regions.exists():
            return Response(
                {"error": f"No regions found of type: {region_type}"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        religious_affiliations = ReligiousAffiliation.objects.filter(region__in=regions)
        serializer = ReligiousAffiliationSerializer(religious_affiliations, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
def get_religious_affiliation_by_region_id(request, region_id):
    """Get religious affiliation data for a specific region.
    
    Args:
        request: HTTP request object
        region_id (str): Entity ID of the region
        
    Returns:
        Response: JSON response containing religious affiliation data
    """
    try:
        region = Region.objects.get(entity_id=region_id)
        religious_affiliation = ReligiousAffiliation.objects.get(region=region)
        serializer = ReligiousAffiliationSerializer(religious_affiliation)
        return Response(serializer.data)
    except Region.DoesNotExist:
        return Response(
            {"error": "Region not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except ReligiousAffiliation.DoesNotExist:
        return Response(
            {"error": "Religious affiliation data not found for this region"}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'regions': {
            'by_type': reverse('get_regions_by_type', args=['province'], request=request),
            'by_id': reverse('get_region_by_id', args=['LK-1'], request=request),
        },
        'population': {
            'by_region_type': reverse('get_population_by_region_type', args=['province'], request=request),
            'by_region_id': reverse('get_population_by_region_id', args=['LK-1'], request=request),
        },
        'age_distribution': {
            'by_region_type': reverse('get_age_distribution_by_region_type', args=['province'], request=request),
            'by_region_id': reverse('get_age_distribution_by_region_id', args=['LK-1'], request=request),
        },
        'ethnicity_distribution': {
            'by_region_type': reverse('get_ethnicity_distribution_by_region_type', args=['province'], request=request),
            'by_region_id': reverse('get_ethnicity_distribution_by_region_id', args=['LK-1'], request=request),
        },
        'gender_distribution': {
            'by_region_type': reverse('get_gender_distribution_by_region_type', args=['province'], request=request),
            'by_region_id': reverse('get_gender_distribution_by_region_id', args=['LK-1'], request=request),
        },
        'marital_status': {
            'by_region_type': reverse('get_marital_status_by_region_type', args=['province'], request=request),
            'by_region_id': reverse('get_marital_status_by_region_id', args=['LK-1'], request=request),
        },
        'religious_affiliation': {
            'by_region_type': reverse('get_religious_affiliation_by_region_type', args=['province'], request=request),
            'by_region_id': reverse('get_religious_affiliation_by_region_id', args=['LK-1'], request=request),
        }
    })

