"""
Core views for authentication and landing page.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group, User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from apps.fleet.models import Vehicle, Route, Trip
from .forms import UserForm
from .roles import ROLE_DESCRIPTIONS, ROLE_PERMISSIONS


def landing(request):
    """Landing page with system overview."""
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
    
    return render(request, 'core/landing.html', context)


def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard:index')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'core/login.html')


@login_required
def logout_view(request):
    """User logout view."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('core:landing')


def _can_manage(request_user, target):
    """Only superusers may modify superuser accounts."""
    return request_user.is_superuser or not target.is_superuser


@login_required
@permission_required('auth.view_user', raise_exception=True)
def user_list(request):
    """List all users."""
    users = User.objects.all().prefetch_related('groups').order_by('username')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    # Role filter
    role_filter = request.GET.get('role', '')
    if role_filter:
        users = users.filter(groups__name=role_filter)

    context = {
        'users': users,
        'search_query': search_query,
        'role_filter': role_filter,
        'roles': list(ROLE_PERMISSIONS),
    }
    return render(request, 'core/user_list.html', context)


@login_required
@permission_required('auth.add_user', raise_exception=True)
def user_create(request):
    """Create a new user and assign a role."""
    if request.method == 'POST':
        form = UserForm(request.POST, request_user=request.user)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User "{user.username}" created successfully.')
            return redirect('core:user_list')
    else:
        form = UserForm(request_user=request.user)

    return render(request, 'core/user_form.html', {'form': form, 'target_user': None})


@login_required
@permission_required('auth.change_user', raise_exception=True)
def user_edit(request, pk):
    """Edit an existing user and their role."""
    target_user = get_object_or_404(User, pk=pk)

    if not _can_manage(request.user, target_user):
        messages.error(request, 'Only superusers can edit superuser accounts.')
        return redirect('core:user_list')

    if request.method == 'POST':
        form = UserForm(request.POST, instance=target_user, request_user=request.user)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User "{user.username}" updated successfully.')
            return redirect('core:user_list')
    else:
        form = UserForm(instance=target_user, request_user=request.user)

    return render(request, 'core/user_form.html', {'form': form, 'target_user': target_user})


@login_required
@permission_required('auth.delete_user', raise_exception=True)
def user_delete(request, pk):
    """Delete a user."""
    target_user = get_object_or_404(User, pk=pk)

    # Prevent deleting yourself
    if target_user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('core:user_list')

    if not _can_manage(request.user, target_user):
        messages.error(request, 'Only superusers can delete superuser accounts.')
        return redirect('core:user_list')

    if request.method == 'POST':
        username = target_user.username
        target_user.delete()
        messages.success(request, f'User "{username}" deleted successfully.')
        return redirect('core:user_list')

    return render(request, 'core/user_confirm_delete.html', {'target_user': target_user})


@login_required
@permission_required('auth.view_group', raise_exception=True)
def role_list(request):
    """Show each role with its permissions and member count."""
    groups = {
        g.name: g for g in Group.objects.filter(name__in=ROLE_PERMISSIONS).prefetch_related('permissions', 'user_set')
    }
    roles = []
    for name in ROLE_PERMISSIONS:
        group = groups.get(name)
        permissions = group.permissions.select_related('content_type').order_by('content_type__model', 'codename') if group else []
        roles.append({
            'name': name,
            'description': ROLE_DESCRIPTIONS.get(name, ''),
            'permissions': permissions,
            'user_count': group.user_set.count() if group else 0,
        })
    return render(request, 'core/role_list.html', {'roles': roles})
