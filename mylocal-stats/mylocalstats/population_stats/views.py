from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from mylocalstats.population_stats.models import Region, TotalPopulation
from mylocalstats.population_stats.serializers import RegionSerializer, TotalPopulationSerializer

@api_view(['GET'])
def get_regions_by_type(request, type):
    try:
        regions = Region.objects.filter(type__iexact=type)
        if not regions.exists():
            return Response(
                {"error": f"No regions found of type: {type}"}, 
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
def get_region_by_id(request, id):
    try:
        region = Region.objects.get(entity_id=id)
        serializer = RegionSerializer(region)
        return Response(serializer.data)
    except Region.DoesNotExist:
        return Response(
            {"error": "Region not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
def get_population_by_region_type(request, type):
    try:
        regions = Region.objects.filter(type__iexact=type)
        if not regions.exists():
            return Response(
                {"error": f"No regions found of type: {type}"}, 
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
