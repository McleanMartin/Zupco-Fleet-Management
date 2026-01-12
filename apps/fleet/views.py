"""
Views for fleet app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Avg
from .models import Vehicle, Location, Route, Trip, FuelRecord
from .forms import VehicleForm, RouteForm, RoutePointForm, TripForm, FuelRecordForm


def landing(request):
    """Landing page."""
    # Get stats for display
    total_vehicles = Vehicle.objects.count()
    active_routes = Route.objects.filter(is_active=True).count()
    active_trips = Trip.objects.filter(status='in_progress').count()
    
    five_min_ago = timezone.now() - timedelta(minutes=5)
    online_vehicles = Vehicle.objects.filter(
        status='active',
        locations__timestamp__gte=five_min_ago
    ).distinct().count()
    
    context = {
        'total_vehicles': total_vehicles,
        'active_routes': active_routes,
        'active_trips': active_trips,
        'online_vehicles': online_vehicles,
    }
    
    return render(request, 'landing.html', context)


def login_view(request):
    """Login view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')


@login_required
def logout_view(request):
    """Logout view."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('landing')


@login_required
def dashboard(request):
    """Main dashboard view with tabs."""
    return render(request, 'fleet/dashboard.html')


@login_required
def stats(request):
    """Return dashboard statistics as HTML partial."""
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
    
    context = {
        'total_vehicles': total_vehicles,
        'active_vehicles': active_vehicles,
        'online_vehicles': online_vehicles,
        'active_routes': active_routes,
        'active_trips': active_trips,
    }
    
    return render(request, 'fleet/partials/stats.html', context)


@login_required
def vehicles(request):
    """Return active vehicles list as HTML partial."""
    vehicles_list = Vehicle.objects.filter(status='active').order_by('registration')
    
    # Get last location for each vehicle
    five_min_ago = timezone.now() - timedelta(minutes=5)
    for vehicle in vehicles_list:
        last_loc = vehicle.locations.order_by('-timestamp').first()
        vehicle.last_location = last_loc
        vehicle.is_online = last_loc and last_loc.timestamp >= five_min_ago if last_loc else False
    
    # Filter by online status if requested (via JavaScript toggle)
    filter_online = request.GET.get('online_only', 'false') == 'true'
    if filter_online:
        vehicles_list = [v for v in vehicles_list if v.is_online]
    
    context = {
        'vehicles': vehicles_list,
    }
    
    return render(request, 'fleet/partials/vehicles.html', context)


@login_required
def routes(request):
    """Return active routes list as HTML partial."""
    routes_list = Route.objects.filter(is_active=True).order_by('code')
    
    # Get point count for each route
    for route in routes_list:
        route.point_count = route.points.count()
    
    context = {
        'routes': routes_list,
    }
    
    return render(request, 'fleet/partials/routes.html', context)


@login_required
def activity(request):
    """Return recent activity as HTML partial."""
    # Get recent locations (last 10)
    recent_locations = Location.objects.select_related('vehicle').order_by('-timestamp')[:10]
    
    context = {
        'recent_locations': recent_locations,
    }
    
    return render(request, 'fleet/partials/activity.html', context)


@login_required
def status(request):
    """Return system status as HTML partial."""
    # Check database connectivity
    try:
        Vehicle.objects.first()
        db_status = 'operational'
        db_status_text = 'Database Connected'
    except Exception:
        db_status = 'error'
        db_status_text = 'Database Error'
    
    # Check recent data
    one_hour_ago = timezone.now() - timedelta(hours=1)
    recent_locations_count = Location.objects.filter(timestamp__gte=one_hour_ago).count()
    
    context = {
        'db_status': db_status,
        'db_status_text': db_status_text,
        'recent_locations_count': recent_locations_count,
    }
    
    return render(request, 'fleet/partials/status.html', context)


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
            }
            vehicle_data['is_online'] = last_loc.timestamp >= five_min_ago
        
        vehicles_data.append(vehicle_data)
    
    return JsonResponse(vehicles_data, safe=False)


@login_required
def fuel(request):
    """Return fuel records as HTML partial."""
    # Get recent fuel records
    fuel_records = FuelRecord.objects.select_related('vehicle').order_by('-date')[:20]
    
    context = {
        'fuel_records': fuel_records,
    }
    
    return render(request, 'fleet/partials/fuel.html', context)


@login_required
def fuel_stats(request):
    """Return fuel statistics as HTML partial."""
    # Last 30 days stats
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    refuels = FuelRecord.objects.filter(
        transaction_type='refuel',
        date__gte=thirty_days_ago
    )
    
    total_fuel = refuels.aggregate(total=Sum('quantity'))['total'] or 0
    total_cost = refuels.aggregate(total=Sum('cost'))['total'] or 0
    avg_cost_per_liter = refuels.aggregate(avg=Avg('cost'))['avg'] or 0
    
    # This month vs last month
    this_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    
    this_month_fuel = FuelRecord.objects.filter(
        transaction_type='refuel',
        date__gte=this_month_start
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    last_month_fuel = FuelRecord.objects.filter(
        transaction_type='refuel',
        date__gte=last_month_start,
        date__lt=this_month_start
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    context = {
        'total_fuel': total_fuel,
        'total_cost': total_cost,
        'avg_cost_per_liter': avg_cost_per_liter,
        'this_month_fuel': this_month_fuel,
        'last_month_fuel': last_month_fuel,
    }
    
    return render(request, 'fleet/partials/fuel_stats.html', context)


# Admin/Management Views
@login_required
def vehicle_list(request):
    """List all vehicles."""
    vehicles_list = Vehicle.objects.all().order_by('registration')
    context = {'vehicles': vehicles_list}
    return render(request, 'fleet/manage/vehicle_list.html', context)


@login_required
def vehicle_create(request):
    """Create a new vehicle."""
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle created successfully.')
            return redirect('vehicle_list')
    else:
        form = VehicleForm()
    return render(request, 'fleet/manage/vehicle_form.html', {'form': form, 'title': 'Add Vehicle'})


@login_required
def vehicle_edit(request, pk):
    """Edit a vehicle."""
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle updated successfully.')
            return redirect('vehicle_list')
    else:
        form = VehicleForm(instance=vehicle)
    return render(request, 'fleet/manage/vehicle_form.html', {'form': form, 'vehicle': vehicle, 'title': 'Edit Vehicle'})


@login_required
def vehicle_delete(request, pk):
    """Delete a vehicle."""
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        vehicle.delete()
        messages.success(request, 'Vehicle deleted successfully.')
        return redirect('vehicle_list')
    return render(request, 'fleet/manage/vehicle_confirm_delete.html', {'vehicle': vehicle})


@login_required
def route_list(request):
    """List all routes."""
    routes_list = Route.objects.all().order_by('code')
    context = {'routes': routes_list}
    return render(request, 'fleet/manage/route_list.html', context)


@login_required
def route_create(request):
    """Create a new route."""
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Route created successfully.')
            return redirect('route_list')
    else:
        form = RouteForm()
    return render(request, 'fleet/manage/route_form.html', {'form': form, 'title': 'Add Route'})


@login_required
def fuel_record_create(request):
    """Create a new fuel record."""
    if request.method == 'POST':
        form = FuelRecordForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fuel record created successfully.')
            return redirect('dashboard')
    else:
        form = FuelRecordForm()
    return render(request, 'fleet/manage/fuel_form.html', {'form': form, 'title': 'Add Fuel Record'})
