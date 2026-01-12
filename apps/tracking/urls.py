"""
URL configuration for tracking app.
"""
from django.urls import path
from . import views

app_name = 'tracking'

urlpatterns = [
    path('', views.tracking_map, name='map'),
    path('locations/', views.location_list, name='locations'),
    path('vehicles/<int:vehicle_pk>/', views.vehicle_tracking, name='vehicle_tracking'),
    path('api/vehicles/', views.vehicles_json, name='vehicles_json'),
    path('api/vehicles/<int:vehicle_pk>/locations/', views.vehicle_locations_json, name='vehicle_locations_json'),
    path('api/trails/', views.all_vehicles_trails_json, name='trails_json'),
]

