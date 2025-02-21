"""
URL configuration for mylocalstats project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from mylocalstats.population_stats import views

# Swagger schema view configuration
schema_view = get_schema_view(
    openapi.Info(
        title="MyLocalStats API",
        default_version='v1',
        description="API for accessing population statistics",
        terms_of_service="https://www.mylocalstats.com/terms/",
        contact=openapi.Contact(email="contact@mylocalstats.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.api_root, name='api-root'),
    
    # Region URLs
    path('api/v1/regions/type/<str:region_type>/', views.get_regions_by_type, name='get_regions_by_type'),
    path('api/v1/region/id/<str:region_id>/', views.get_region_by_id, name='get_region_by_id'),
    
    # Population URLs
    path('api/v1/population/type/<str:region_type>/', views.get_population_by_region_type, name='get_population_by_region_type'),
    path('api/v1/population/id/<str:region_id>/', views.get_population_by_region_id, name='get_population_by_region_id'),
    
    # Age Distribution URLs
    path('api/v1/age-distribution/type/<str:region_type>/', views.get_age_distribution_by_region_type, name='get_age_distribution_by_region_type'),
    path('api/v1/age-distribution/id/<str:region_id>/', views.get_age_distribution_by_region_id, name='get_age_distribution_by_region_id'),
    
    # Ethnicity Distribution URLs
    path('api/v1/ethnicity-distribution/type/<str:region_type>/', views.get_ethnicity_distribution_by_region_type, name='get_ethnicity_distribution_by_region_type'),
    path('api/v1/ethnicity-distribution/id/<str:region_id>/', views.get_ethnicity_distribution_by_region_id, name='get_ethnicity_distribution_by_region_id'),
    
    # Gender Distribution URLs
    path('api/v1/gender-distribution/type/<str:region_type>/', views.get_gender_distribution_by_region_type, name='get_gender_distribution_by_region_type'),
    path('api/v1/gender-distribution/id/<str:region_id>/', views.get_gender_distribution_by_region_id, name='get_gender_distribution_by_region_id'),

    # Marital Status URLs
    path('api/v1/marital-status/type/<str:region_type>/', views.get_marital_status_by_region_type, name='get_marital_status_by_region_type'),
    path('api/v1/marital-status/id/<str:region_id>/', views.get_marital_status_by_region_id, name='get_marital_status_by_region_id'),

    # Religious Affiliation URLs
    path('api/v1/religious-affiliation/type/<str:region_type>/', views.get_religious_affiliation_by_region_type, name='get_religious_affiliation_by_region_type'),
    path('api/v1/religious-affiliation/id/<str:region_id>/', views.get_religious_affiliation_by_region_id, name='get_religious_affiliation_by_region_id'),

    # GraphQL URLs
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True))),
    
    # Swagger URLs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', 
            schema_view.without_ui(cache_timeout=0), 
            name='schema-json'),
    path('swagger/', 
         schema_view.with_ui('swagger', cache_timeout=0), 
         name='schema-swagger-ui'),
    path('redoc/', 
         schema_view.with_ui('redoc', cache_timeout=0), 
         name='schema-redoc'),
]