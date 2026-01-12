"""
Views for vehicle management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from apps.fleet.models import Vehicle, Location
from apps.fleet.forms import VehicleForm


@login_required
def vehicle_list(request):
    """List all vehicles with filtering and search."""
    vehicles = Vehicle.objects.all().order_by('registration')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        vehicles = vehicles.filter(
            Q(registration__icontains=search_query) |
            Q(make__icontains=search_query) |
            Q(model__icontains=search_query)
        )
    
    # Status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        vehicles = vehicles.filter(status=status_filter)
    
    # Get additional data for each vehicle (annotate with computed values)
    # Note: last_location and is_online are properties, so we can't assign them
    # They are accessed directly as properties in templates
    five_min_ago = timezone.now() - timedelta(minutes=5)
    for vehicle in vehicles:
        # These are regular attributes, so they can be set
        vehicle.trip_count = vehicle.trips.count()
        vehicle.location_count = vehicle.locations.count()
    
    context = {
        'vehicles': vehicles,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': Vehicle.STATUS_CHOICES,
    }
    return render(request, 'vehicles/list.html', context)


@login_required
def vehicle_detail(request, pk):
    """View detailed information about a specific vehicle."""
    vehicle = get_object_or_404(Vehicle, pk=pk)
    
    # Get recent locations
    recent_locations = vehicle.locations.order_by('-timestamp')[:50]
    
    # Get recent trips
    recent_trips = vehicle.trips.order_by('-scheduled_start')[:10]
    
    # Get fuel records
    fuel_records = vehicle.fuel_records.order_by('-date')[:20]
    
    # Calculate statistics
    five_min_ago = timezone.now() - timedelta(minutes=5)
    last_loc = vehicle.locations.order_by('-timestamp').first()
    is_online = last_loc and last_loc.timestamp >= five_min_ago if last_loc else False
    
    context = {
        'vehicle': vehicle,
        'recent_locations': recent_locations,
        'recent_trips': recent_trips,
        'fuel_records': fuel_records,
        'is_online': is_online,
        'last_location': last_loc,
    }
    return render(request, 'vehicles/detail.html', context)


@login_required
def vehicle_create(request):
    """Create a new vehicle."""
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save()
            messages.success(request, f'Vehicle {vehicle.registration} created successfully.')
            return redirect('vehicles:detail', pk=vehicle.pk)
    else:
        form = VehicleForm()
    
    context = {
        'form': form,
        'title': 'Add Vehicle',
        'action': 'Create',
    }
    return render(request, 'vehicles/form.html', context)


@login_required
def vehicle_edit(request, pk):
    """Edit an existing vehicle."""
    vehicle = get_object_or_404(Vehicle, pk=pk)
    
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            vehicle = form.save()
            messages.success(request, f'Vehicle {vehicle.registration} updated successfully.')
            return redirect('vehicles:detail', pk=vehicle.pk)
    else:
        form = VehicleForm(instance=vehicle)
    
    context = {
        'form': form,
        'vehicle': vehicle,
        'title': 'Edit Vehicle',
        'action': 'Update',
    }
    return render(request, 'vehicles/form.html', context)


@login_required
def vehicle_delete(request, pk):
    """Delete a vehicle."""
    vehicle = get_object_or_404(Vehicle, pk=pk)
    
    if request.method == 'POST':
        registration = vehicle.registration
        vehicle.delete()
        messages.success(request, f'Vehicle {registration} deleted successfully.')
        return redirect('vehicles:list')
    
    context = {
        'vehicle': vehicle,
    }
    return render(request, 'vehicles/confirm_delete.html', context)


@login_required
def vehicle_json(request):
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
