"""
URL configuration for ZUPCO IoT Fleet Management System.
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # API (REST Framework)
    path('api/', include('apps.api.urls')),
    
    # Core (authentication, landing, user management)
    path('', include('apps.core.urls')),
    
    # Dashboard
    path('dashboard/', include('apps.dashboard.urls')),
    
    # Feature apps with namespaces
    path('vehicles/', include('apps.vehicles.urls')),
    path('routes/', include('apps.routes.urls')),
    path('fuel/', include('apps.fuel.urls')),
    path('tracking/', include('apps.tracking.urls')),
    path('trips/', include('apps.trips.urls')),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

