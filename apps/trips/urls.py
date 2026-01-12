"""
URL configuration for trips app.
"""
from django.urls import path
from . import views

app_name = 'trips'

urlpatterns = [
    path('', views.trip_list, name='list'),
    path('add/', views.trip_create, name='create'),
    path('<int:pk>/', views.trip_detail, name='detail'),
    path('<int:pk>/edit/', views.trip_edit, name='edit'),
    path('<int:pk>/delete/', views.trip_delete, name='delete'),
    path('<int:pk>/start/', views.trip_start, name='start'),
    path('<int:pk>/complete/', views.trip_complete, name='complete'),
    path('<int:pk>/cancel/', views.trip_cancel, name='cancel'),
]

