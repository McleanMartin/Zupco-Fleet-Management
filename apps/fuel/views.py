"""
Views for fuel management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Avg, Count
from apps.fleet.models import FuelRecord, Vehicle
from apps.fleet.forms import FuelRecordForm


@login_required
@permission_required('fleet.view_fuelrecord', raise_exception=True)
def fuel_list(request):
    """List all fuel records with filtering."""
    fuel_records = FuelRecord.objects.select_related('vehicle').order_by('-date')
    
    # Vehicle filter
    vehicle_id = request.GET.get('vehicle', '')
    if vehicle_id:
        fuel_records = fuel_records.filter(vehicle_id=vehicle_id)
    
    # Transaction type filter
    transaction_type = request.GET.get('type', '')
    if transaction_type:
        fuel_records = fuel_records.filter(transaction_type=transaction_type)
    
    # Date range filter
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if date_from:
        fuel_records = fuel_records.filter(date__gte=date_from)
    if date_to:
        fuel_records = fuel_records.filter(date__lte=date_to)
    
    vehicles = Vehicle.objects.all().order_by('registration')
    
    context = {
        'fuel_records': fuel_records[:100],  # Limit to 100 most recent
        'vehicles': vehicles,
        'vehicle_filter': vehicle_id,
        'transaction_type_filter': transaction_type,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'fuel/list.html', context)


@login_required
@permission_required('fleet.view_fuelrecord', raise_exception=True)
def fuel_detail(request, pk):
    """View detailed information about a specific fuel record."""
    fuel_record = get_object_or_404(FuelRecord, pk=pk)
    
    # Get related fuel records for the same vehicle
    related_records = FuelRecord.objects.filter(
        vehicle=fuel_record.vehicle
    ).exclude(pk=pk).order_by('-date')[:10]
    
    context = {
        'fuel_record': fuel_record,
        'related_records': related_records,
    }
    return render(request, 'fuel/detail.html', context)


@login_required
@permission_required('fleet.add_fuelrecord', raise_exception=True)
def fuel_create(request):
    """Create a new fuel record."""
    if request.method == 'POST':
        form = FuelRecordForm(request.POST)
        if form.is_valid():
            fuel_record = form.save()
            messages.success(request, 'Fuel record created successfully.')
            return redirect('fuel:detail', pk=fuel_record.pk)
    else:
        form = FuelRecordForm()
    
    context = {
        'form': form,
        'title': 'Add Fuel Record',
        'action': 'Create',
    }
    return render(request, 'fuel/form.html', context)


@login_required
@permission_required('fleet.change_fuelrecord', raise_exception=True)
def fuel_edit(request, pk):
    """Edit an existing fuel record."""
    fuel_record = get_object_or_404(FuelRecord, pk=pk)
    
    if request.method == 'POST':
        form = FuelRecordForm(request.POST, instance=fuel_record)
        if form.is_valid():
            fuel_record = form.save()
            messages.success(request, 'Fuel record updated successfully.')
            return redirect('fuel:detail', pk=fuel_record.pk)
    else:
        form = FuelRecordForm(instance=fuel_record)
    
    context = {
        'form': form,
        'fuel_record': fuel_record,
        'title': 'Edit Fuel Record',
        'action': 'Update',
    }
    return render(request, 'fuel/form.html', context)


@login_required
@permission_required('fleet.delete_fuelrecord', raise_exception=True)
def fuel_delete(request, pk):
    """Delete a fuel record."""
    fuel_record = get_object_or_404(FuelRecord, pk=pk)
    
    if request.method == 'POST':
        fuel_record.delete()
        messages.success(request, 'Fuel record deleted successfully.')
        return redirect('fuel:list')
    
    context = {
        'fuel_record': fuel_record,
    }
    return render(request, 'fuel/confirm_delete.html', context)


@login_required
@permission_required('fleet.view_fuelrecord', raise_exception=True)
def fuel_stats(request):
    """Display fuel statistics and analytics."""
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
    
    # Per vehicle statistics
    vehicle_stats = FuelRecord.objects.filter(
        transaction_type='refuel',
        date__gte=thirty_days_ago
    ).values('vehicle__registration', 'vehicle__make', 'vehicle__model').annotate(
        total_fuel=Sum('quantity'),
        total_cost=Sum('cost'),
        record_count=Count('id')
    ).order_by('-total_fuel')[:10]
    
    context = {
        'total_fuel': total_fuel,
        'total_cost': total_cost,
        'avg_cost_per_liter': avg_cost_per_liter,
        'this_month_fuel': this_month_fuel,
        'last_month_fuel': last_month_fuel,
        'vehicle_stats': vehicle_stats,
    }
    return render(request, 'fuel/stats.html', context)
