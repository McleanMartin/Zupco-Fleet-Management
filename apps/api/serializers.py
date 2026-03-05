"""
Serializers for API endpoints.
"""
from rest_framework import serializers
from apps.fleet.models import Vehicle, Location, Route, RoutePoint, Trip


class VehicleSerializer(serializers.ModelSerializer):
    """Serializer for Vehicle model."""
    last_location = serializers.SerializerMethodField()
    is_online = serializers.SerializerMethodField()
    
    class Meta:
        model = Vehicle
        fields = [
            'id', 'registration', 'make', 'model', 'year', 'capacity',
            'status', 'last_location', 'is_online', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_last_location(self, obj):
        last_loc = obj.last_location
        if last_loc:
            return {
                'latitude': float(last_loc.latitude),
                'longitude': float(last_loc.longitude),
                'speed': last_loc.speed,
                'timestamp': last_loc.timestamp.isoformat()
            }
        return None
    
    def get_is_online(self, obj):
        return obj.is_online


class LocationSerializer(serializers.ModelSerializer):
    """Serializer for Location model."""
    vehicle_registration = serializers.CharField(source='vehicle.registration', read_only=True)
    registration = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = Location
        fields = [
            'id', 'vehicle', 'registration', 'vehicle_registration', 'latitude', 'longitude',
            'speed', 'heading', 'timestamp', 'battery', 'ignition'
        ]
        read_only_fields = ['id', 'timestamp', 'vehicle_registration']
        extra_kwargs = {
            'vehicle': {'required': False, 'allow_null': True}
        }
    
    def validate(self, data):
        """Resolve registration to vehicle ID if provided."""
        registration = data.pop('registration', None)
        
        # If registration provided, use it to lookup vehicle
        if registration:
            try:
                vehicle = Vehicle.objects.get(registration=registration)
                # Check if vehicle is active
                if vehicle.status != 'active':
                    raise serializers.ValidationError("Vehicle must be active to receive location data.")
                data['vehicle'] = vehicle
            except Vehicle.DoesNotExist:
                raise serializers.ValidationError(f"Vehicle with registration '{registration}' not found.")
        else:
            # If vehicle is provided by ID, check its status
            vehicle = data.get('vehicle')
            if vehicle and vehicle.status != 'active':
                raise serializers.ValidationError("Vehicle must be active to receive location data.")
        
        # Validate that vehicle is provided (either directly or via registration)
        if 'vehicle' not in data or data.get('vehicle') is None:
            raise serializers.ValidationError("Either 'vehicle' ID or 'registration' must be provided.")
        
        return data


class RouteSerializer(serializers.ModelSerializer):
    """Serializer for Route model."""
    point_count = serializers.IntegerField(source='points.count', read_only=True)
    
    class Meta:
        model = Route
        fields = [
            'id', 'name', 'code', 'description', 'is_active',
            'point_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RoutePointSerializer(serializers.ModelSerializer):
    """Serializer for RoutePoint model."""
    route_code = serializers.CharField(source='route.code', read_only=True)
    
    class Meta:
        model = RoutePoint
        fields = [
            'id', 'route', 'route_code', 'sequence', 'latitude', 'longitude',
            'name', 'scheduled_time'
        ]
        read_only_fields = ['id']


class TripSerializer(serializers.ModelSerializer):
    """Serializer for Trip model."""
    vehicle_registration = serializers.CharField(source='vehicle.registration', read_only=True)
    route_code = serializers.CharField(source='route.code', read_only=True, allow_null=True)
    duration_minutes = serializers.FloatField(read_only=True)
    delay_minutes = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Trip
        fields = [
            'id', 'vehicle', 'vehicle_registration', 'route', 'route_code',
            'start_time', 'end_time', 'scheduled_start', 'scheduled_end',
            'status', 'duration_minutes', 'delay_minutes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

