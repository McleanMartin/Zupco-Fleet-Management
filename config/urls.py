"""
URL configuration for ZUPCO IoT Fleet Management System.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', include('fleet.urls')),
]

# Customize admin site header
admin.site.site_header = 'ZUPCO Fleet Management Admin'
admin.site.site_title = 'ZUPCO Admin'
admin.site.index_title = 'Fleet Management System'

