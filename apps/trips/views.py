"""
Views for trip management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from apps.fleet.models import Trip, Vehicle, Route
from apps.fleet.forms import TripForm


@login_required
@permission_required('fleet.view_trip', raise_exception=True)
def trip_list(request):
    """List all trips with filtering."""
    trips = Trip.objects.select_related('vehicle', 'route').order_by('-scheduled_start')
    
    # Status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        trips = trips.filter(status=status_filter)
    
    # Vehicle filter
    vehicle_id = request.GET.get('vehicle', '')
    if vehicle_id:
        trips = trips.filter(vehicle_id=vehicle_id)
    
    # Route filter
    route_id = request.GET.get('route', '')
    if route_id:
        trips = trips.filter(route_id=route_id)
    
    # Date range filter
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if date_from:
        trips = trips.filter(scheduled_start__gte=date_from)
    if date_to:
        trips = trips.filter(scheduled_start__lte=date_to)
    
    vehicles = Vehicle.objects.filter(status='active').order_by('registration')
    routes = Route.objects.filter(is_active=True).order_by('code')
    
    context = {
        'trips': trips[:200],  # Limit to 200 most recent
        'vehicles': vehicles,
        'routes': routes,
        'status_filter': status_filter,
        'vehicle_filter': vehicle_id,
        'route_filter': route_id,
        'date_from': date_from,
        'date_to': date_to,
        'status_choices': Trip.STATUS_CHOICES,
    }
    return render(request, 'trips/list.html', context)


@login_required
@permission_required('fleet.view_trip', raise_exception=True)
def trip_detail(request, pk):
    """View detailed information about a specific trip."""
    trip = get_object_or_404(Trip.objects.select_related('vehicle', 'route'), pk=pk)
    
    # Get location history for the trip time period (if available)
    locations = []
    if trip.start_time and trip.end_time:
        locations = trip.vehicle.locations.filter(
            timestamp__gte=trip.start_time,
            timestamp__lte=trip.end_time
        ).order_by('timestamp')
    elif trip.start_time:
        locations = trip.vehicle.locations.filter(
            timestamp__gte=trip.start_time
        ).order_by('timestamp')[:100]
    
    # Get related trips
    related_trips = Trip.objects.filter(
        vehicle=trip.vehicle
    ).exclude(pk=pk).order_by('-scheduled_start')[:10]
    
    context = {
        'trip': trip,
        'locations': locations,
        'related_trips': related_trips,
    }
    return render(request, 'trips/detail.html', context)


@login_required
@permission_required('fleet.add_trip', raise_exception=True)
def trip_create(request):
    """Create a new trip."""
    if request.method == 'POST':
        form = TripForm(request.POST)
        if form.is_valid():
            trip = form.save()
            messages.success(request, f'Trip created successfully.')
            return redirect('trips:detail', pk=trip.pk)
    else:
        form = TripForm()
    
    context = {
        'form': form,
        'title': 'Schedule Trip',
        'action': 'Create',
    }
    return render(request, 'trips/form.html', context)


@login_required
@permission_required('fleet.change_trip', raise_exception=True)
def trip_edit(request, pk):
    """Edit an existing trip."""
    trip = get_object_or_404(Trip, pk=pk)
    
    if request.method == 'POST':
        form = TripForm(request.POST, instance=trip)
        if form.is_valid():
            trip = form.save()
            messages.success(request, 'Trip updated successfully.')
            return redirect('trips:detail', pk=trip.pk)
    else:
        form = TripForm(instance=trip)
    
    context = {
        'form': form,
        'trip': trip,
        'title': 'Edit Trip',
        'action': 'Update',
    }
    return render(request, 'trips/form.html', context)


@login_required
@permission_required('fleet.delete_trip', raise_exception=True)
def trip_delete(request, pk):
    """Delete a trip."""
    trip = get_object_or_404(Trip, pk=pk)
    
    if request.method == 'POST':
        trip.delete()
        messages.success(request, 'Trip deleted successfully.')
        return redirect('trips:list')
    
    context = {
        'trip': trip,
    }
    return render(request, 'trips/confirm_delete.html', context)


@login_required
@permission_required('fleet.change_trip', raise_exception=True)
def trip_start(request, pk):
    """Start a trip."""
    trip = get_object_or_404(Trip, pk=pk)
    
    if trip.status == 'scheduled':
        trip.status = 'in_progress'
        trip.start_time = timezone.now()
        trip.save()
        messages.success(request, f'Trip started successfully.')
    else:
        messages.error(request, f'Cannot start trip. Current status: {trip.get_status_display()}')
    
    return redirect('trips:detail', pk=trip.pk)


@login_required
@permission_required('fleet.change_trip', raise_exception=True)
def trip_complete(request, pk):
    """Complete a trip."""
    trip = get_object_or_404(Trip, pk=pk)
    
    if trip.status == 'in_progress':
        trip.status = 'completed'
        trip.end_time = timezone.now()
        trip.save()
        messages.success(request, f'Trip completed successfully.')
    else:
        messages.error(request, f'Cannot complete trip. Current status: {trip.get_status_display()}')
    
    return redirect('trips:detail', pk=trip.pk)


@login_required
@permission_required('fleet.change_trip', raise_exception=True)
def trip_cancel(request, pk):
    """Cancel a trip."""
    trip = get_object_or_404(Trip, pk=pk)
    
    if trip.status in ['scheduled', 'in_progress']:
        trip.status = 'cancelled'
        if not trip.end_time:
            trip.end_time = timezone.now()
        trip.save()
        messages.success(request, f'Trip cancelled successfully.')
    else:
        messages.error(request, f'Cannot cancel trip. Current status: {trip.get_status_display()}')
    
    return redirect('trips:detail', pk=trip.pk)
