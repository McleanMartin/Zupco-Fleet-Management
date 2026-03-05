"""
Tests for API endpoints.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.fleet.models import Vehicle
import json


class LocationCreateAPITests(TestCase):
    """Test the location create endpoint with vehicle registration and ID."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        
        # Create a test vehicle
        self.vehicle = Vehicle.objects.create(
            registration="TEST-001",
            make="Toyota",
            model="Hiace",
            year=2023,
            capacity=15,
            status='active'
        )
    
    def test_create_location_with_registration(self):
        """Test creating a location using vehicle registration (preferred)."""
        data = {
            'registration': 'TEST-001',
            'latitude': -17.8292,
            'longitude': 31.0522,
            'speed': 45.5,
            'ignition': True
        }
        
        response = self.client.post(
            '/api/locations/create/',
            data,
            format='json'
        )
        
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Response: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['vehicle_registration'], 'TEST-001')
        self.assertEqual(float(response.data['latitude']), -17.8292)
        self.assertEqual(float(response.data['longitude']), 31.0522)
    
    def test_create_location_with_vehicle_id(self):
        """Test creating a location using vehicle ID (backward compatibility)."""
        data = {
            'vehicle': self.vehicle.id,
            'latitude': -17.8292,
            'longitude': 31.0522,
            'speed': 45.5,
            'ignition': True
        }
        
        response = self.client.post(
            '/api/locations/create/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['vehicle_registration'], 'TEST-001')
    
    def test_create_location_invalid_registration(self):
        """Test creating a location with non-existent registration."""
        data = {
            'registration': 'INVALID-999',
            'latitude': -17.8292,
            'longitude': 31.0522,
            'speed': 45.5,
            'ignition': True
        }
        
        response = self.client.post(
            '/api/locations/create/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_location_no_vehicle_identifier(self):
        """Test creating a location without vehicle ID or registration."""
        data = {
            'latitude': -17.8292,
            'longitude': 31.0522,
            'speed': 45.5,
            'ignition': True
        }
        
        response = self.client.post(
            '/api/locations/create/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_location_inactive_vehicle(self):
        """Test creating a location for an inactive vehicle."""
        # Create an inactive vehicle
        inactive_vehicle = Vehicle.objects.create(
            registration="INACTIVE-001",
            make="Toyota",
            model="Hiace",
            year=2023,
            capacity=15,
            status='inactive'
        )
        
        data = {
            'registration': 'INACTIVE-001',
            'latitude': -17.8292,
            'longitude': 31.0522,
            'speed': 45.5,
            'ignition': True
        }
        
        response = self.client.post(
            '/api/locations/create/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LocationFilterTests(TestCase):
    """Test filtering locations by registration and vehicle ID."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        
        # Create test vehicles
        self.vehicle1 = Vehicle.objects.create(
            registration="VEH-001",
            make="Toyota",
            model="Hiace",
            year=2023,
            capacity=15,
            status='active'
        )
        
        self.vehicle2 = Vehicle.objects.create(
            registration="VEH-002",
            make="Toyota",
            model="Hiace",
            year=2023,
            capacity=15,
            status='active'
        )
    
    def test_filter_locations_by_registration(self):
        """Test filtering locations by vehicle registration."""
        # Create locations
        from apps.fleet.models import Location
        Location.objects.create(
            vehicle=self.vehicle1,
            latitude=-17.8292,
            longitude=31.0522,
            speed=45.5,
            ignition=True
        )
        Location.objects.create(
            vehicle=self.vehicle2,
            latitude=-17.8350,
            longitude=31.0600,
            speed=50.0,
            ignition=True
        )
        
        # Filter by registration
        response = self.client.get('/api/locations/?registration=VEH-001')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['vehicle_registration'], 'VEH-001')
    
    def test_filter_locations_by_vehicle_id(self):
        """Test filtering locations by vehicle ID (backward compatibility)."""
        # Create locations
        from apps.fleet.models import Location
        Location.objects.create(
            vehicle=self.vehicle1,
            latitude=-17.8292,
            longitude=31.0522,
            speed=45.5,
            ignition=True
        )
        Location.objects.create(
            vehicle=self.vehicle2,
            latitude=-17.8350,
            longitude=31.0600,
            speed=50.0,
            ignition=True
        )
        
        # Filter by vehicle ID
        response = self.client.get(f'/api/locations/?vehicle={self.vehicle1.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['vehicle_registration'], 'VEH-001')
