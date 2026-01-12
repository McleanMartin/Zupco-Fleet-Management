"""
Views for dashboard and analytics.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Sum, Avg, Q
from apps.fleet.models import Vehicle, Location, Route, Trip, FuelRecord


@login_required
def dashboard_index(request):
    """Main dashboard view with overview statistics."""
    return render(request, 'dashboard/index.html')


@login_required
def dashboard_stats(request):
    """Return dashboard statistics as partial HTML."""
    total_vehicles = Vehicle.objects.count()
    active_vehicles = Vehicle.objects.filter(status='active').count()
    
    # Count online vehicles (reported location in last 5 minutes)
    five_min_ago = timezone.now() - timedelta(minutes=5)
    online_vehicles = Vehicle.objects.filter(
        status='active',
        locations__timestamp__gte=five_min_ago
    ).distinct().count()
    
    # Count active routes
    active_routes = Route.objects.filter(is_active=True).count()
    
    # Count in-progress trips
    active_trips = Trip.objects.filter(status='in_progress').count()
    
    # Recent activity count (last hour)
    one_hour_ago = timezone.now() - timedelta(hours=1)
    recent_locations = Location.objects.filter(timestamp__gte=one_hour_ago).count()
    
    context = {
        'total_vehicles': total_vehicles,
        'active_vehicles': active_vehicles,
        'online_vehicles': online_vehicles,
        'active_routes': active_routes,
        'active_trips': active_trips,
        'recent_locations': recent_locations,
    }
    
    return render(request, 'dashboard/partials/stats.html', context)


@login_required
def dashboard_vehicles(request):
    """Return active vehicles list as partial HTML."""
    vehicles_list = Vehicle.objects.filter(status='active').order_by('registration')
    
    # Get last location for each vehicle
    five_min_ago = timezone.now() - timedelta(minutes=5)
    for vehicle in vehicles_list:
        last_loc = vehicle.locations.order_by('-timestamp').first()
        vehicle.last_location = last_loc
        vehicle.is_online = last_loc and last_loc.timestamp >= five_min_ago if last_loc else False
    
    # Filter by online status if requested
    filter_online = request.GET.get('online_only', 'false') == 'true'
    if filter_online:
        vehicles_list = [v for v in vehicles_list if v.is_online]
    
    context = {
        'vehicles': vehicles_list,
    }
    
    return render(request, 'dashboard/partials/vehicles.html', context)


@login_required
def dashboard_routes(request):
    """Return active routes list as partial HTML."""
    routes_list = Route.objects.filter(is_active=True).order_by('code')
    
    # Get point count for each route
    for route in routes_list:
        route.point_count = route.points.count()
        route.active_trip_count = route.trips.filter(status='in_progress').count()
    
    context = {
        'routes': routes_list,
    }
    
    return render(request, 'dashboard/partials/routes.html', context)


@login_required
def dashboard_activity(request):
    """Return recent activity as partial HTML."""
    # Get recent locations (last 20)
    recent_locations = Location.objects.select_related('vehicle').order_by('-timestamp')[:20]
    
    context = {
        'recent_locations': recent_locations,
    }
    
    return render(request, 'dashboard/partials/activity.html', context)


@login_required
def dashboard_status(request):
    """Return system status as partial HTML."""
    # Check database connectivity
    try:
        Vehicle.objects.first()
        db_status = 'operational'
        db_status_text = 'Database Connected'
    except Exception as e:
        db_status = 'error'
        db_status_text = f'Database Error: {str(e)}'
    
    # Check recent data
    one_hour_ago = timezone.now() - timedelta(hours=1)
    recent_locations_count = Location.objects.filter(timestamp__gte=one_hour_ago).count()
    
    # Check API status (simple check)
    api_status = 'operational'
    api_status_text = 'API Active'
    
    context = {
        'db_status': db_status,
        'db_status_text': db_status_text,
        'api_status': api_status,
        'api_status_text': api_status_text,
        'recent_locations_count': recent_locations_count,
    }
    
    return render(request, 'dashboard/partials/status.html', context)


@login_required
def dashboard_analytics(request):
    """Advanced analytics and reporting dashboard."""
    # Vehicle statistics
    vehicle_stats = Vehicle.objects.aggregate(
        total=Count('id'),
        active=Count('id', filter=Q(status='active')),
        maintenance=Count('id', filter=Q(status='maintenance')),
        inactive=Count('id', filter=Q(status='inactive'))
    )
    
    # Trip statistics (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    trip_stats = Trip.objects.filter(
        scheduled_start__gte=thirty_days_ago
    ).aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(status='completed')),
        in_progress=Count('id', filter=Q(status='in_progress')),
        cancelled=Count('id', filter=Q(status='cancelled'))
    )
    
    # Fuel statistics (last 30 days)
    fuel_stats = FuelRecord.objects.filter(
        transaction_type='refuel',
        date__gte=thirty_days_ago
    ).aggregate(
        total_fuel=Sum('quantity'),
        total_cost=Sum('cost'),
        avg_cost=Avg('cost')
    )
    
    # Route statistics
    route_stats = Route.objects.aggregate(
        total=Count('id'),
        active=Count('id', filter=Q(is_active=True))
    )
    
    context = {
        'vehicle_stats': vehicle_stats,
        'trip_stats': trip_stats,
        'fuel_stats': fuel_stats,
        'route_stats': route_stats,
    }
    
    return render(request, 'dashboard/analytics.html', context)
