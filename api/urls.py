"""
URL configuration for API endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VehicleViewSet, LocationViewSet, LocationCreateView,
    RouteViewSet, RoutePointViewSet, TripViewSet
)

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'locations', LocationViewSet, basename='location')
router.register(r'routes', RouteViewSet, basename='route')
router.register(r'route-points', RoutePointViewSet, basename='routepoint')
router.register(r'trips', TripViewSet, basename='trip')

urlpatterns = [
    path('', include(router.urls)),
    # Simple endpoint for IoT devices (ESP32)
    path('locations/create/', LocationCreateView.as_view(), name='location-create'),
]

