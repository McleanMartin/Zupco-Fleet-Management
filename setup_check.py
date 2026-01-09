"""
Quick setup verification script for ZUPCO Fleet Management System.
Run this after initial setup to verify everything is configured correctly.
"""
import os
import sys
import django

def check_setup():
    """Check if Django project is set up correctly."""
    print("ZUPCO Fleet Management - Setup Verification")
    print("=" * 50)
    
    # Check Python version
    print(f"\n✓ Python version: {sys.version}")
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("\n✗ Error: manage.py not found. Run this script from the project root.")
        return False
    
    # Try to set up Django
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()
        print("✓ Django configured successfully")
    except Exception as e:
        print(f"\n✗ Error configuring Django: {e}")
        print("  Make sure you've installed dependencies: pip install -r requirements.txt")
        return False
    
    # Check if database exists
    if os.path.exists('db.sqlite3'):
        print("✓ Database file exists")
    else:
        print("⚠ Database file not found. Run: python manage.py migrate")
    
    # Check installed apps
    from django.conf import settings
    required_apps = ['fleet', 'api', 'rest_framework']
    missing_apps = [app for app in required_apps if app not in settings.INSTALLED_APPS]
    
    if missing_apps:
        print(f"✗ Missing apps in INSTALLED_APPS: {missing_apps}")
        return False
    else:
        print("✓ All required apps are installed")
    
    # Check models
    try:
        from fleet.models import Vehicle, Location, Route, RoutePoint, Trip
        print("✓ All models imported successfully")
    except Exception as e:
        print(f"✗ Error importing models: {e}")
        return False
    
    # Check API views
    try:
        from api.views import LocationCreateView
        print("✓ API views imported successfully")
    except Exception as e:
        print(f"✗ Error importing API views: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("Setup verification complete!")
    print("\nNext steps:")
    print("1. Run migrations: python manage.py migrate")
    print("2. Create superuser: python manage.py createsuperuser")
    print("3. Start server: python manage.py runserver")
    print("4. Access admin: http://127.0.0.1:8000/admin/")
    print("5. Test API: http://127.0.0.1:8000/api/")
    
    return True

if __name__ == "__main__":
    success = check_setup()
    sys.exit(0 if success else 1)

