"""
URL configuration for dashboard app.
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_analytics, name='index'),
    path('api/stats/', views.dashboard_stats, name='stats'),
    path('api/vehicles/', views.dashboard_vehicles, name='vehicles'),
    path('api/routes/', views.dashboard_routes, name='routes'),
    path('api/activity/', views.dashboard_activity, name='activity'),
    path('api/status/', views.dashboard_status, name='status'),
]

