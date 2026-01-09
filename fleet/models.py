"""
Core models for ZUPCO IoT Fleet Management System.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Vehicle(models.Model):
    """Represents a vehicle in the ZUPCO fleet."""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('maintenance', 'In Maintenance'),
        ('inactive', 'Inactive'),
    ]
    
    registration = models.CharField(max_length=20, unique=True, help_text="Vehicle registration number")
    make = models.CharField(max_length=50, help_text="Vehicle manufacturer")
    model = models.CharField(max_length=50, help_text="Vehicle model")
    year = models.IntegerField(
        validators=[MinValueValidator(1990), MaxValueValidator(2030)],
        help_text="Manufacturing year"
    )
    capacity = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1)],
        help_text="Passenger capacity"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text="Current operational status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['registration']
        verbose_name = 'Vehicle'
        verbose_name_plural = 'Vehicles'
    
    def __str__(self):
        return f"{self.registration} - {self.make} {self.model} ({self.year})"
    
    @property
    def last_location(self):
        """Get the most recent location for this vehicle."""
        return self.location_set.order_by('-timestamp').first()
    
    @property
    def is_online(self):
        """Check if vehicle has reported location in last 5 minutes."""
        from django.utils import timezone
        from datetime import timedelta
        
        last_loc = self.last_location
        if not last_loc:
            return False
        
        five_min_ago = timezone.now() - timedelta(minutes=5)
        return last_loc.timestamp >= five_min_ago


class Location(models.Model):
    """GPS location data from IoT devices."""
    
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='locations',
        help_text="Vehicle this location belongs to"
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="Latitude coordinate"
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="Longitude coordinate"
    )
    speed = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="Speed in km/h"
    )
    heading = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(360.0)],
        help_text="Heading in degrees (0-360)"
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    battery = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
        help_text="Battery voltage"
    )
    ignition = models.BooleanField(
        default=False,
        help_text="Ignition status"
    )
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['vehicle', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'
    
    def __str__(self):
        return f"{self.vehicle.registration} @ ({self.latitude}, {self.longitude}) - {self.timestamp}"


class Route(models.Model):
    """Represents a bus route in the ZUPCO network."""
    
    name = models.CharField(max_length=100, help_text="Route name (e.g., 'City Centre to Chitungwiza')")
    code = models.CharField(
        max_length=10,
        unique=True,
        help_text="Route code (e.g., 'RT17')"
    )
    description = models.TextField(blank=True, help_text="Route description")
    is_active = models.BooleanField(
        default=True,
        help_text="Whether route is currently active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['code']
        verbose_name = 'Route'
        verbose_name_plural = 'Routes'
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class RoutePoint(models.Model):
    """Individual stops/points along a route."""
    
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name='points',
        help_text="Route this point belongs to"
    )
    sequence = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Order of this point in the route (1, 2, 3, ...)"
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="Latitude coordinate"
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="Longitude coordinate"
    )
    name = models.CharField(
        max_length=100,
        help_text="Stop/point name"
    )
    scheduled_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Scheduled arrival time at this point"
    )
    
    class Meta:
        ordering = ['route', 'sequence']
        unique_together = [['route', 'sequence']]
        verbose_name = 'Route Point'
        verbose_name_plural = 'Route Points'
    
    def __str__(self):
        return f"{self.route.code} - Point {self.sequence}: {self.name}"


class Trip(models.Model):
    """Represents a scheduled or active trip."""
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='trips',
        help_text="Vehicle assigned to this trip"
    )
    route = models.ForeignKey(
        Route,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trips',
        help_text="Route for this trip"
    )
    start_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Actual trip start time"
    )
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Actual trip end time"
    )
    scheduled_start = models.DateTimeField(
        help_text="Scheduled trip start time"
    )
    scheduled_end = models.DateTimeField(
        help_text="Scheduled trip end time"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        help_text="Current trip status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_start']
        indexes = [
            models.Index(fields=['vehicle', '-scheduled_start']),
            models.Index(fields=['status', '-scheduled_start']),
        ]
        verbose_name = 'Trip'
        verbose_name_plural = 'Trips'
    
    def __str__(self):
        return f"Trip {self.id}: {self.vehicle.registration} on {self.route.code if self.route else 'No Route'} - {self.status}"
    
    @property
    def duration_minutes(self):
        """Calculate trip duration in minutes."""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds() / 60
        return None
    
    @property
    def delay_minutes(self):
        """Calculate delay from scheduled start time."""
        if self.start_time:
            delta = self.start_time - self.scheduled_start
            return delta.total_seconds() / 60
        return None


class FuelRecord(models.Model):
    """Fuel consumption and refueling records."""
    
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='fuel_records',
        help_text="Vehicle this fuel record belongs to"
    )
    date = models.DateTimeField(
        help_text="Date and time of fuel transaction"
    )
    fuel_type = models.CharField(
        max_length=20,
        choices=[
            ('diesel', 'Diesel'),
            ('petrol', 'Petrol'),
            ('electric', 'Electric'),
        ],
        default='diesel',
        help_text="Type of fuel"
    )
    quantity = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="Fuel quantity in liters"
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.0)],
        help_text="Cost in local currency"
    )
    odometer_reading = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Odometer reading at time of refueling"
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=[
            ('refuel', 'Refuel'),
            ('consumption', 'Consumption'),
        ],
        default='refuel',
        help_text="Type of transaction"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['vehicle', '-date']),
            models.Index(fields=['-date']),
        ]
        verbose_name = 'Fuel Record'
        verbose_name_plural = 'Fuel Records'
    
    def __str__(self):
        return f"{self.vehicle.registration} - {self.quantity}L @ {self.date}"
    
    @property
    def cost_per_liter(self):
        """Calculate cost per liter."""
        if self.quantity > 0:
            return float(self.cost) / self.quantity
        return 0.0

