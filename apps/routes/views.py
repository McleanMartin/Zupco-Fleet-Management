"""
Views for route management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Count
from apps.fleet.models import Route, RoutePoint, Trip
from apps.fleet.forms import RouteForm, RoutePointForm


@login_required
@permission_required('fleet.view_route', raise_exception=True)
def route_list(request):
    """List all routes with filtering."""
    routes = Route.objects.all().order_by('code')
    
    # Active filter
    active_filter = request.GET.get('active', '')
    if active_filter == 'true':
        routes = routes.filter(is_active=True)
    elif active_filter == 'false':
        routes = routes.filter(is_active=False)
    
    # Add statistics for each route
    for route in routes:
        route.point_count = route.points.count()
        route.trip_count = route.trips.count()
        route.active_trip_count = route.trips.filter(status='in_progress').count()
    
    context = {
        'routes': routes,
        'active_filter': active_filter,
    }
    return render(request, 'routes/list.html', context)


@login_required
@permission_required('fleet.view_route', raise_exception=True)
def route_detail(request, pk):
    """View detailed information about a specific route."""
    route = get_object_or_404(Route, pk=pk)
    route_points = route.points.order_by('sequence')
    recent_trips = route.trips.order_by('-scheduled_start')[:20]
    
    context = {
        'route': route,
        'route_points': route_points,
        'recent_trips': recent_trips,
    }
    return render(request, 'routes/detail.html', context)


@login_required
@permission_required('fleet.add_route', raise_exception=True)
def route_create(request):
    """Create a new route."""
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            route = form.save()
            messages.success(request, f'Route {route.code} created successfully.')
            return redirect('routes:detail', pk=route.pk)
    else:
        form = RouteForm()
    
    context = {
        'form': form,
        'title': 'Add Route',
        'action': 'Create',
    }
    return render(request, 'routes/form.html', context)


@login_required
@permission_required('fleet.change_route', raise_exception=True)
def route_edit(request, pk):
    """Edit an existing route."""
    route = get_object_or_404(Route, pk=pk)
    
    if request.method == 'POST':
        form = RouteForm(request.POST, instance=route)
        if form.is_valid():
            route = form.save()
            messages.success(request, f'Route {route.code} updated successfully.')
            return redirect('routes:detail', pk=route.pk)
    else:
        form = RouteForm(instance=route)
    
    context = {
        'form': form,
        'route': route,
        'title': 'Edit Route',
        'action': 'Update',
    }
    return render(request, 'routes/form.html', context)


@login_required
@permission_required('fleet.delete_route', raise_exception=True)
def route_delete(request, pk):
    """Delete a route."""
    route = get_object_or_404(Route, pk=pk)
    
    if request.method == 'POST':
        code = route.code
        route.delete()
        messages.success(request, f'Route {code} deleted successfully.')
        return redirect('routes:list')
    
    context = {
        'route': route,
    }
    return render(request, 'routes/confirm_delete.html', context)


@login_required
@permission_required('fleet.add_routepoint', raise_exception=True)
def route_point_create(request, route_pk):
    """Add a point to a route."""
    route = get_object_or_404(Route, pk=route_pk)
    
    if request.method == 'POST':
        form = RoutePointForm(request.POST)
        if form.is_valid():
            route_point = form.save(commit=False)
            route_point.route = route
            route_point.save()
            messages.success(request, f'Route point added successfully.')
            return redirect('routes:detail', pk=route.pk)
    else:
        form = RoutePointForm(initial={'route': route})
    
    context = {
        'form': form,
        'route': route,
        'title': 'Add Route Point',
        'action': 'Add',
    }
    return render(request, 'routes/point_form.html', context)


@login_required
@permission_required('fleet.change_routepoint', raise_exception=True)
def route_point_edit(request, route_pk, point_pk):
    """Edit a route point."""
    route = get_object_or_404(Route, pk=route_pk)
    route_point = get_object_or_404(RoutePoint, pk=point_pk, route=route)
    
    if request.method == 'POST':
        form = RoutePointForm(request.POST, instance=route_point)
        if form.is_valid():
            form.save()
            messages.success(request, 'Route point updated successfully.')
            return redirect('routes:detail', pk=route.pk)
    else:
        form = RoutePointForm(instance=route_point)
    
    context = {
        'form': form,
        'route': route,
        'route_point': route_point,
        'title': 'Edit Route Point',
        'action': 'Update',
    }
    return render(request, 'routes/point_form.html', context)


@login_required
@permission_required('fleet.delete_routepoint', raise_exception=True)
def route_point_delete(request, route_pk, point_pk):
    """Delete a route point."""
    route = get_object_or_404(Route, pk=route_pk)
    route_point = get_object_or_404(RoutePoint, pk=point_pk, route=route)
    
    if request.method == 'POST':
        route_point.delete()
        messages.success(request, 'Route point deleted successfully.')
        return redirect('routes:detail', pk=route.pk)
    
    context = {
        'route': route,
        'route_point': route_point,
    }
    return render(request, 'routes/point_confirm_delete.html', context)
