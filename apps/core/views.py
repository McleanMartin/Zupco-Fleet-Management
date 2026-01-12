"""
Core views for authentication and landing page.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from apps.fleet.models import Vehicle, Route, Trip


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


def is_staff(user):
    """Check if user is staff."""
    return user.is_staff


@login_required
@user_passes_test(is_staff)
def user_list(request):
    """List all users."""
    users = User.objects.all().order_by('username')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    context = {
        'users': users,
        'search_query': search_query,
    }
    return render(request, 'core/user_list.html', context)


@login_required
@user_passes_test(is_staff)
def user_create(request):
    """Create a new user."""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        is_staff = request.POST.get('is_staff') == 'on'
        is_superuser = request.POST.get('is_superuser') == 'on'
        
        # Validate
        if not username:
            messages.error(request, 'Username is required.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif password != password_confirm:
            messages.error(request, 'Passwords do not match.')
        elif not password:
            messages.error(request, 'Password is required.')
        else:
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_staff=is_staff,
                    is_superuser=is_superuser
                )
                messages.success(request, f'User "{user.username}" created successfully.')
                return redirect('core:user_list')
            except Exception as e:
                messages.error(request, f'Error creating user: {str(e)}')
    
    return render(request, 'core/user_form.html', {'user': None})


@login_required
@user_passes_test(is_staff)
def user_edit(request, pk):
    """Edit an existing user."""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        is_staff = request.POST.get('is_staff') == 'on'
        is_superuser = request.POST.get('is_superuser') == 'on'
        
        # Validate username
        if not username:
            messages.error(request, 'Username is required.')
        elif User.objects.filter(username=username).exclude(pk=user.pk).exists():
            messages.error(request, 'Username already exists.')
        else:
            # Update user
            user.username = username
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.is_staff = is_staff
            user.is_superuser = is_superuser
            
            # Update password if provided
            if password:
                if password != password_confirm:
                    messages.error(request, 'Passwords do not match.')
                    return render(request, 'core/user_form.html', {'user': user})
                user.set_password(password)
            
            try:
                user.save()
                messages.success(request, f'User "{user.username}" updated successfully.')
                return redirect('core:user_list')
            except Exception as e:
                messages.error(request, f'Error updating user: {str(e)}')
    
    return render(request, 'core/user_form.html', {'user': user})


@login_required
@user_passes_test(is_staff)
def user_delete(request, pk):
    """Delete a user."""
    user = get_object_or_404(User, pk=pk)
    
    # Prevent deleting yourself
    if user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('core:user_list')
    
    if request.method == 'POST':
        username = user.username
        try:
            user.delete()
            messages.success(request, f'User "{username}" deleted successfully.')
            return redirect('core:user_list')
        except Exception as e:
            messages.error(request, f'Error deleting user: {str(e)}')
            return redirect('core:user_list')
    
    return render(request, 'core/user_confirm_delete.html', {'user': user})
