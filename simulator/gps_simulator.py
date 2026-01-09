"""
GPS Simulator for ZUPCO Fleet Management System.

This script simulates GPS data from vehicles moving along routes.
Useful for development, testing, and research data generation.
"""
import requests
import random
import time
import math
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class GPSSimulator:
    """Simulates GPS data for vehicles moving along routes."""
    
    def __init__(self, api_url: str = "http://localhost:8000/api/locations/create/"):
        """
        Initialize the GPS simulator.
        
        Args:
            api_url: Base URL for the Django API endpoint
        """
        self.api_url = api_url
        self.running = False
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula.
        Returns distance in kilometers.
        """
        R = 6371  # Earth's radius in kilometers
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def interpolate_point(self, start: Dict, end: Dict, progress: float) -> Dict:
        """
        Interpolate a point between start and end based on progress (0.0 to 1.0).
        
        Args:
            start: Dict with 'lat' and 'lon'
            end: Dict with 'lat' and 'lon'
            progress: Float between 0.0 and 1.0
        
        Returns:
            Dict with 'lat' and 'lon'
        """
        lat = start['lat'] + (end['lat'] - start['lat']) * progress
        lon = start['lon'] + (end['lon'] - start['lon']) * progress
        
        # Add small random noise to simulate GPS inaccuracy
        lat += random.uniform(-0.0005, 0.0005)
        lon += random.uniform(-0.0005, 0.0005)
        
        return {'lat': lat, 'lon': lon}
    
    def send_location(self, vehicle_id: int, lat: float, lon: float, 
                     speed: float, heading: Optional[float] = None,
                     ignition: bool = True, battery: Optional[float] = None) -> bool:
        """
        Send location data to the API.
        
        Returns:
            True if successful, False otherwise
        """
        data = {
            'vehicle': vehicle_id,
            'latitude': lat,
            'longitude': lon,
            'speed': speed,
            'ignition': ignition,
        }
        
        if heading is not None:
            data['heading'] = heading
        
        if battery is not None:
            data['battery'] = battery
        
        try:
            response = requests.post(self.api_url, json=data, timeout=5)
            if response.status_code in [200, 201]:
                return True
            else:
                print(f"Error: API returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Error sending location: {e}")
            return False
    
    def simulate_vehicle_route(self, vehicle_id: int, route_points: List[Dict],
                               interval: int = 30, speed_range: tuple = (20, 60),
                               loop: bool = True):
        """
        Simulate a vehicle moving along a route.
        
        Args:
            vehicle_id: ID of the vehicle in the database
            route_points: List of dicts with 'lat' and 'lon' keys
            interval: Seconds between location updates
            speed_range: Tuple of (min_speed, max_speed) in km/h
            loop: Whether to loop back to start after completing route
        """
        if not route_points or len(route_points) < 2:
            print("Error: Need at least 2 route points")
            return
        
        self.running = True
        current_segment = 0
        segment_progress = 0.0
        
        print(f"Starting simulation for vehicle {vehicle_id}")
        print(f"Route has {len(route_points)} points")
        
        while self.running:
            # Get current segment endpoints
            start_point = route_points[current_segment]
            end_point = route_points[(current_segment + 1) % len(route_points)]
            
            # Calculate current position
            position = self.interpolate_point(start_point, end_point, segment_progress)
            
            # Calculate speed (varies based on progress in segment)
            base_speed = random.uniform(speed_range[0], speed_range[1])
            # Slow down near stops
            if segment_progress > 0.8:
                base_speed *= 0.5
            
            # Calculate heading (direction to next point)
            lat1, lon1 = start_point['lat'], start_point['lon']
            lat2, lon2 = end_point['lat'], end_point['lon']
            heading = math.degrees(math.atan2(
                math.radians(lat2 - lat1),
                math.radians(lon2 - lon1)
            ))
            
            # Send location
            success = self.send_location(
                vehicle_id=vehicle_id,
                lat=position['lat'],
                lon=position['lon'],
                speed=base_speed,
                heading=heading,
                ignition=True,
                battery=12.5 + random.uniform(-0.5, 0.5)
            )
            
            if success:
                print(f"Vehicle {vehicle_id}: ({position['lat']:.6f}, {position['lon']:.6f}) "
                      f"Speed: {base_speed:.1f} km/h")
            
            # Update progress
            segment_progress += 0.1  # Move 10% along segment each update
            
            if segment_progress >= 1.0:
                # Move to next segment
                current_segment += 1
                segment_progress = 0.0
                
                # Check if route is complete
                if current_segment >= len(route_points) - 1:
                    if loop:
                        current_segment = 0
                        print(f"Vehicle {vehicle_id}: Completed route, looping...")
                    else:
                        print(f"Vehicle {vehicle_id}: Route completed")
                        break
            
            time.sleep(interval)
    
    def simulate_multiple_vehicles(self, vehicle_routes: Dict[int, List[Dict]],
                                   interval: int = 30):
        """
        Simulate multiple vehicles on different routes.
        
        Args:
            vehicle_routes: Dict mapping vehicle_id to list of route points
            interval: Seconds between location updates
        """
        import threading
        
        threads = []
        for vehicle_id, route_points in vehicle_routes.items():
            thread = threading.Thread(
                target=self.simulate_vehicle_route,
                args=(vehicle_id, route_points, interval),
                daemon=True
            )
            thread.start()
            threads.append(thread)
            time.sleep(1)  # Stagger start times
        
        print(f"Started {len(threads)} vehicle simulations")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping simulations...")
            self.running = False
            for thread in threads:
                thread.join(timeout=5)


# Example usage and sample routes for Harare, Zimbabwe
if __name__ == "__main__":
    # Sample route: City Centre to Chitungwiza (approximate coordinates)
    # These are example coordinates - replace with actual ZUPCO route data
    route_cc_to_chitungwiza = [
        {'lat': -17.8292, 'lon': 31.0522},  # City Centre
        {'lat': -17.8400, 'lon': 31.0600},  # Intermediate stop 1
        {'lat': -17.8500, 'lon': 31.0700},  # Intermediate stop 2
        {'lat': -17.8600, 'lon': 31.0800},  # Intermediate stop 3
        {'lat': -17.8700, 'lon': 31.0900},  # Chitungwiza
    ]
    
    # Sample route: City Centre to Epworth
    route_cc_to_epworth = [
        {'lat': -17.8292, 'lon': 31.0522},  # City Centre
        {'lat': -17.8200, 'lon': 31.0500},  # Intermediate stop
        {'lat': -17.8100, 'lon': 31.0450},  # Epworth
    ]
    
    simulator = GPSSimulator()
    
    # Example: Simulate one vehicle
    # simulator.simulate_vehicle_route(
    #     vehicle_id=1,
    #     route_points=route_cc_to_chitungwiza,
    #     interval=30,  # Update every 30 seconds
    #     speed_range=(25, 55),  # 25-55 km/h
    #     loop=True
    # )
    
    # Example: Simulate multiple vehicles
    vehicle_routes = {
        1: route_cc_to_chitungwiza,
        2: route_cc_to_epworth,
    }
    
    print("GPS Simulator for ZUPCO Fleet Management")
    print("=" * 50)
    print("\nTo use this simulator:")
    print("1. Make sure Django server is running (python manage.py runserver)")
    print("2. Create vehicles in the admin interface or via API")
    print("3. Update vehicle_routes dict with actual vehicle IDs")
    print("4. Run: python simulator/gps_simulator.py")
    print("\nFor single vehicle simulation, uncomment the example above.")
    print("\nNote: Replace sample coordinates with actual ZUPCO route data.")

