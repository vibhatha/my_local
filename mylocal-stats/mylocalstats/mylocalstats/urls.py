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
from django.urls import path

from mylocalstats.population_stats import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('regions/type/<str:type>/', views.get_regions_by_type, name='regions-by-type'),
    path('region/<int:region_id>/', views.get_region_by_id, name='region-by-id'),
    path('population/region-type/<str:type>/', views.get_population_by_region_type, name='population-by-region-type'),
    path('population/region/<int:region_id>/', views.get_population_by_region_id, name='population-by-region-id'),
]
