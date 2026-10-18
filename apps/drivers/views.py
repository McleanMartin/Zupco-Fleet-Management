"""
Views for driver management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q
from apps.fleet.models import Driver
from apps.fleet.forms import DriverForm


@login_required
@permission_required('fleet.view_driver', raise_exception=True)
def driver_list(request):
    """List all drivers with search and status filter."""
    drivers = Driver.objects.select_related('user', 'assigned_vehicle')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        drivers = drivers.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(employee_number__icontains=search_query) |
            Q(license_number__icontains=search_query) |
            Q(assigned_vehicle__registration__icontains=search_query)
        )

    # Status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        drivers = drivers.filter(status=status_filter)

    context = {
        'drivers': drivers,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': Driver.STATUS_CHOICES,
    }
    return render(request, 'drivers/list.html', context)


@login_required
@permission_required('fleet.add_driver', raise_exception=True)
def driver_create(request):
    """Create a new driver, optionally with a login account."""
    if request.method == 'POST':
        form = DriverForm(request.POST)
        if form.is_valid():
            driver = form.save()
            messages.success(request, f'Driver {driver.full_name} created successfully.')
            return redirect('drivers:list')
    else:
        form = DriverForm()

    context = {
        'form': form,
        'title': 'Add Driver',
        'action': 'Create',
    }
    return render(request, 'drivers/form.html', context)


@login_required
@permission_required('fleet.change_driver', raise_exception=True)
def driver_edit(request, pk):
    """Edit an existing driver."""
    driver = get_object_or_404(Driver, pk=pk)

    if request.method == 'POST':
        form = DriverForm(request.POST, instance=driver)
        if form.is_valid():
            driver = form.save()
            messages.success(request, f'Driver {driver.full_name} updated successfully.')
            return redirect('drivers:list')
    else:
        form = DriverForm(instance=driver)

    context = {
        'form': form,
        'driver': driver,
        'title': 'Edit Driver',
        'action': 'Update',
    }
    return render(request, 'drivers/form.html', context)


@login_required
@permission_required('fleet.delete_driver', raise_exception=True)
def driver_delete(request, pk):
    """Delete a driver and deactivate their login account."""
    driver = get_object_or_404(Driver, pk=pk)

    if request.method == 'POST':
        name = driver.full_name
        if driver.user:
            driver.user.is_active = False
            driver.user.save(update_fields=['is_active'])
        driver.delete()
        messages.success(request, f'Driver {name} deleted successfully.')
        return redirect('drivers:list')

    return render(request, 'drivers/confirm_delete.html', {'driver': driver})
