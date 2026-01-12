"""
URL configuration for routes app.
"""
from django.urls import path
from . import views

app_name = 'routes'

urlpatterns = [
    path('', views.route_list, name='list'),
    path('add/', views.route_create, name='create'),
    path('<int:pk>/', views.route_detail, name='detail'),
    path('<int:pk>/edit/', views.route_edit, name='edit'),
    path('<int:pk>/delete/', views.route_delete, name='delete'),
    path('<int:route_pk>/points/add/', views.route_point_create, name='point_create'),
    path('<int:route_pk>/points/<int:point_pk>/edit/', views.route_point_edit, name='point_edit'),
    path('<int:route_pk>/points/<int:point_pk>/delete/', views.route_point_delete, name='point_delete'),
]

