"""
Views for vehicle tracking and real-time monitoring.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta, datetime, date
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from apps.fleet.models import Vehicle, Location
from itertools import groupby
from operator import itemgetter


@login_required
def tracking_map(request):
    """Real-time vehicle tracking map view."""
    vehicles = Vehicle.objects.filter(status='active')
    
    context = {
        'vehicles': vehicles,
    }
    return render(request, 'tracking/map.html', context)


@login_required
def location_list(request):
    """List all location records with filtering and grouping by date."""
    locations = Location.objects.select_related('vehicle').order_by('-timestamp')
    
    # Vehicle filter - support both registration (preferred) and ID
    registration = request.GET.get('registration', '')
    vehicle_id = request.GET.get('vehicle', '')
    
    if registration:
        locations = locations.filter(vehicle__registration=registration)
    elif vehicle_id:
        locations = locations.filter(vehicle_id=vehicle_id)
    
    # Date filter
    date_filter = request.GET.get('date', '')
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            filter_start = timezone.make_aware(datetime.combine(filter_date, datetime.min.time()))
            filter_end = timezone.make_aware(datetime.combine(filter_date, datetime.max.time()))
            locations = locations.filter(timestamp__gte=filter_start, timestamp__lte=filter_end)
        except (ValueError, TypeError):
            date_filter = ''
    else:
        # Default to last 24 hours if no date specified
        time_threshold = timezone.now() - timedelta(hours=24)
        locations = locations.filter(timestamp__gte=time_threshold)
    
    # Time range filter (only used if no specific date is selected)
    if not date_filter:
        hours = request.GET.get('hours', '24')
        try:
            hours = int(hours)
            time_threshold = timezone.now() - timedelta(hours=hours)
            locations = locations.filter(timestamp__gte=time_threshold)
        except (ValueError, TypeError):
            hours = 24
    else:
        hours = 24
    
    # Online only filter
    online_only = request.GET.get('online', '')
    if online_only == 'true':
        five_min_ago = timezone.now() - timedelta(minutes=5)
        vehicle_ids = Vehicle.objects.filter(
            locations__timestamp__gte=five_min_ago
        ).distinct().values_list('id', flat=True)
        locations = locations.filter(vehicle_id__in=vehicle_ids)
    
    # Convert to list and group by date
    locations_list = list(locations[:500])
    grouped_locations = {}
    
    for location in locations_list:
        location_date = location.timestamp.date()
        if location_date not in grouped_locations:
            grouped_locations[location_date] = []
        grouped_locations[location_date].append(location)
    
    # Get available dates for the date picker
    available_dates = Location.objects.filter(vehicle_id=vehicle_id if vehicle_id else None).values_list('timestamp', flat=True).distinct().order_by('-timestamp')[:100] if vehicle_id or registration else []
    available_dates = sorted(set([d.date() for d in available_dates]), reverse=True)
    
    vehicles = Vehicle.objects.filter(status='active').order_by('registration')
    
    context = {
        'locations': locations_list,
        'grouped_locations': dict(sorted(grouped_locations.items(), reverse=True)),
        'available_dates': available_dates,
        'vehicles': vehicles,
        'registration_filter': registration,
        'vehicle_filter': vehicle_id,
        'hours_filter': hours,
        'online_filter': online_only,
        'date_filter': date_filter,
    }
    return render(request, 'tracking/locations.html', context)


@login_required
def vehicle_tracking(request, vehicle_pk):
    """Track a specific vehicle's location history."""
    vehicle = get_object_or_404(Vehicle, pk=vehicle_pk)
    
    # Get location history
    hours = request.GET.get('hours', '24')
    try:
        hours = int(hours)
        time_threshold = timezone.now() - timedelta(hours=hours)
        locations = vehicle.locations.filter(timestamp__gte=time_threshold).order_by('-timestamp')
    except (ValueError, TypeError):
        locations = vehicle.locations.order_by('-timestamp')[:100]
    
    # Get last location
    last_location = vehicle.locations.order_by('-timestamp').first()
    
    # Check if online
    five_min_ago = timezone.now() - timedelta(minutes=5)
    is_online = last_location and last_location.timestamp >= five_min_ago if last_location else False
    
    context = {
        'vehicle': vehicle,
        'locations': locations,
        'last_location': last_location,
        'is_online': is_online,
        'hours_filter': hours if isinstance(hours, int) else 24,
    }
    return render(request, 'tracking/vehicle_tracking.html', context)


@login_required
def vehicles_json(request):
    """Return vehicles as JSON for map updates."""
    vehicles_list = Vehicle.objects.filter(status='active')
    
    five_min_ago = timezone.now() - timedelta(minutes=5)
    vehicles_data = []
    
    for vehicle in vehicles_list:
        last_loc = vehicle.locations.order_by('-timestamp').first()
        
        vehicle_data = {
            'id': vehicle.id,
            'registration': vehicle.registration,
            'make': vehicle.make,
            'model': vehicle.model,
            'status': vehicle.status,
            'is_online': False,
            'last_location': None,
        }
        
        if last_loc:
            vehicle_data['last_location'] = {
                'latitude': str(last_loc.latitude),
                'longitude': str(last_loc.longitude),
                'speed': last_loc.speed,
                'heading': last_loc.heading if last_loc.heading is not None else None,
                'timestamp': last_loc.timestamp.isoformat(),
                'ignition': last_loc.ignition,
                'battery': last_loc.battery,
            }
            vehicle_data['is_online'] = last_loc.timestamp >= five_min_ago
        
        vehicles_data.append(vehicle_data)
    
    return JsonResponse(vehicles_data, safe=False)


@login_required
def vehicle_locations_json(request, vehicle_pk):
    """Return location history for a specific vehicle as JSON."""
    vehicle = get_object_or_404(Vehicle, pk=vehicle_pk)
    
    hours = request.GET.get('hours', '24')
    try:
        hours = int(hours)
        time_threshold = timezone.now() - timedelta(hours=hours)
        locations = vehicle.locations.filter(timestamp__gte=time_threshold).order_by('timestamp')
    except (ValueError, TypeError):
        locations = vehicle.locations.order_by('-timestamp')[:100]
    
    locations_data = []
    for location in locations:
        locations_data.append({
            'latitude': str(location.latitude),
            'longitude': str(location.longitude),
            'speed': location.speed,
            'heading': location.heading,
            'timestamp': location.timestamp.isoformat(),
            'ignition': location.ignition,
            'battery': location.battery,
        })
    
    return JsonResponse(locations_data, safe=False)


@login_required
def all_vehicles_trails_json(request):
    """Return location trails for a specific vehicle within a datetime range."""
    vehicle_id = request.GET.get('vehicle_id')
    start_datetime_str = request.GET.get('start_datetime')
    end_datetime_str = request.GET.get('end_datetime')
    
    # Parse datetime strings
    try:
        if start_datetime_str:
            start_datetime = parse_datetime(start_datetime_str)
            if start_datetime and timezone.is_naive(start_datetime):
                start_datetime = timezone.make_aware(start_datetime)
        else:
            # Default to 24 hours ago if not provided
            start_datetime = timezone.now() - timedelta(hours=24)
        
        if end_datetime_str:
            end_datetime = parse_datetime(end_datetime_str)
            if end_datetime and timezone.is_naive(end_datetime):
                end_datetime = timezone.make_aware(end_datetime)
        else:
            # Default to now if not provided
            end_datetime = timezone.now()
    except (ValueError, TypeError):
        # Fallback to last 24 hours
        end_datetime = timezone.now()
        start_datetime = end_datetime - timedelta(hours=24)
    
    # Validate date range
    if start_datetime > end_datetime:
        start_datetime, end_datetime = end_datetime, start_datetime
    
    trails_data = {}
    
    # Get vehicle if vehicle_id is provided
    if vehicle_id:
        try:
            vehicle = get_object_or_404(Vehicle, pk=vehicle_id, status='active')
            vehicles_list = [vehicle]
        except (ValueError, TypeError):
            return JsonResponse({}, safe=False)
    else:
        return JsonResponse({}, safe=False)  # Require vehicle_id
    
    for vehicle in vehicles_list:
        locations = vehicle.locations.filter(
            timestamp__gte=start_datetime,
            timestamp__lte=end_datetime
        ).order_by('timestamp')[:1000]  # Limit to 1000 points per vehicle
        
        if locations.exists():
            trail_points = []
            for location in locations:
                trail_points.append({
                    'latitude': float(location.latitude),
                    'longitude': float(location.longitude),
                    'timestamp': location.timestamp.isoformat(),
                    'speed': location.speed,
                })
            
            trails_data[vehicle.id] = {
                'vehicle_id': vehicle.id,
                'registration': vehicle.registration,
                'make': vehicle.make,
                'model': vehicle.model,
                'points': trail_points,
            }
    
    return JsonResponse(trails_data, safe=False)
