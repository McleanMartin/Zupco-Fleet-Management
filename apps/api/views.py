"""
API views for ZUPCO Fleet Management System.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta

from apps.fleet.models import Vehicle, Location, Route, RoutePoint, Trip
from .serializers import (
    VehicleSerializer, LocationSerializer, RouteSerializer,
    RoutePointSerializer, TripSerializer
)


class VehicleViewSet(viewsets.ModelViewSet):
    """ViewSet for Vehicle model."""
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    
    @action(detail=True, methods=['get'])
    def locations(self, request, pk=None):
        """Get recent locations for a vehicle."""
        vehicle = self.get_object()
        hours = int(request.query_params.get('hours', 24))
        
        since = timezone.now() - timedelta(hours=hours)
        locations = vehicle.locations.filter(timestamp__gte=since).order_by('-timestamp')
        
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data)


class LocationViewSet(viewsets.ModelViewSet):
    """ViewSet for Location model."""
    queryset = Location.objects.all().select_related('vehicle')
    serializer_class = LocationSerializer
    
    def get_queryset(self):
        """Filter locations by vehicle if provided."""
        queryset = super().get_queryset()
        vehicle_id = self.request.query_params.get('vehicle', None)
        hours = int(self.request.query_params.get('hours', 24))
        
        since = timezone.now() - timedelta(hours=hours)
        queryset = queryset.filter(timestamp__gte=since)
        
        if vehicle_id:
            queryset = queryset.filter(vehicle_id=vehicle_id)
        
        return queryset.order_by('-timestamp')
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent locations for all vehicles (last 5 minutes)."""
        five_min_ago = timezone.now() - timedelta(minutes=5)
        
        # Get most recent location for each vehicle
        vehicles = Vehicle.objects.filter(status='active')
        recent_locations = []
        
        for vehicle in vehicles:
            last_loc = vehicle.locations.filter(timestamp__gte=five_min_ago).first()
            if last_loc:
                recent_locations.append(last_loc)
        
        serializer = self.get_serializer(recent_locations, many=True)
        return Response(serializer.data)


class LocationCreateView(APIView):
    """Simple endpoint for IoT devices to POST location data."""
    
    def post(self, request):
        """Create a new location entry from IoT device."""
        serializer = LocationSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RouteViewSet(viewsets.ModelViewSet):
    """ViewSet for Route model."""
    queryset = Route.objects.all().prefetch_related('points')
    serializer_class = RouteSerializer
    
    def get_queryset(self):
        """Filter by active status if provided."""
        queryset = super().get_queryset()
        active_only = self.request.query_params.get('active', None)
        
        if active_only == 'true':
            queryset = queryset.filter(is_active=True)
        
        return queryset


class RoutePointViewSet(viewsets.ModelViewSet):
    """ViewSet for RoutePoint model."""
    queryset = RoutePoint.objects.all().select_related('route')
    serializer_class = RoutePointSerializer
    
    def get_queryset(self):
        """Filter by route if provided."""
        queryset = super().get_queryset()
        route_id = self.request.query_params.get('route', None)
        
        if route_id:
            queryset = queryset.filter(route_id=route_id)
        
        return queryset.order_by('route', 'sequence')


class TripViewSet(viewsets.ModelViewSet):
    """ViewSet for Trip model."""
    queryset = Trip.objects.all().select_related('vehicle', 'route')
    serializer_class = TripSerializer
    
    def get_queryset(self):
        """Filter trips by status, vehicle, or route."""
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status', None)
        vehicle_id = self.request.query_params.get('vehicle', None)
        route_id = self.request.query_params.get('route', None)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if vehicle_id:
            queryset = queryset.filter(vehicle_id=vehicle_id)
        if route_id:
            queryset = queryset.filter(route_id=route_id)
        
        return queryset

