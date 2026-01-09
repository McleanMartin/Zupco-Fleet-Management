"""
URL configuration for fleet app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # API endpoints (for HTMX)
    path('api/stats/', views.stats, name='stats'),
    path('api/vehicles/', views.vehicles, name='vehicles'),
    path('api/routes/', views.routes, name='routes'),
    path('api/activity/', views.activity, name='activity'),
    path('api/status/', views.status, name='status'),
    path('api/fuel/', views.fuel, name='fuel'),
    path('api/fuel/stats/', views.fuel_stats, name='fuel_stats'),
    path('api/vehicles.json', views.vehicles_json, name='vehicles_json'),
    
    # Management views
    path('manage/vehicles/', views.vehicle_list, name='vehicle_list'),
    path('manage/vehicles/add/', views.vehicle_create, name='vehicle_create'),
    path('manage/vehicles/<int:pk>/edit/', views.vehicle_edit, name='vehicle_edit'),
    path('manage/vehicles/<int:pk>/delete/', views.vehicle_delete, name='vehicle_delete'),
    path('manage/routes/', views.route_list, name='route_list'),
    path('manage/routes/add/', views.route_create, name='route_create'),
    path('manage/fuel/add/', views.fuel_record_create, name='fuel_record_create'),
]
