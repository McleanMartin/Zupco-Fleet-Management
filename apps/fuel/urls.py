"""
URL configuration for fuel app.
"""
from django.urls import path
from . import views

app_name = 'fuel'

urlpatterns = [
    path('', views.fuel_list, name='list'),
    path('stats/', views.fuel_stats, name='stats'),
    path('add/', views.fuel_create, name='create'),
    path('<int:pk>/', views.fuel_detail, name='detail'),
    path('<int:pk>/edit/', views.fuel_edit, name='edit'),
    path('<int:pk>/delete/', views.fuel_delete, name='delete'),
]

