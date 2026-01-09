# Installation Guide

## Prerequisites

### Required Software

1. **Python 3.8 or higher**
   - Download from: https://www.python.org/downloads/
   - Verify installation: `python --version`

2. **pip** (Python package manager)
   - Usually included with Python
   - Verify: `pip --version`

3. **Git** (optional, for version control)
   - Download from: https://git-scm.com/downloads

### Optional but Recommended

- **Virtual Environment**: Python venv module (included with Python 3.3+)
- **Code Editor**: VS Code, PyCharm, or any Python IDE
- **Database Tool**: DB Browser for SQLite (for viewing database)

## Installation Steps

### Step 1: Clone or Download Project

**Option A: If using Git**
```bash
git clone <repository-url>
cd box
```

**Option B: If downloaded as ZIP**
```bash
# Extract ZIP file
cd box
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Note**: Your prompt should show `(venv)` when activated.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Django 4.2+
- Django REST Framework
- django-cors-headers
- requests (for GPS simulator)

### Step 4: Verify Installation

Run the setup check script:
```bash
python setup_check.py
```

Expected output:
```
✓ Python version: 3.x.x
✓ Django configured successfully
✓ All required apps are installed
✓ All models imported successfully
✓ API views imported successfully
```

### Step 5: Initialize Database

```bash
python manage.py migrate
```

This creates the SQLite database file (`db.sqlite3`) and all necessary tables.

### Step 6: Create Superuser

```bash
python manage.py createsuperuser
```

Follow prompts to create an admin account:
- Username
- Email (optional)
- Password

### Step 7: Start Development Server

```bash
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### Step 8: Verify Installation

1. **Admin Interface**: http://127.0.0.1:8000/admin/
   - Login with superuser credentials
   - You should see Fleet, API sections

2. **API Root**: http://127.0.0.1:8000/api/
   - Should show browsable API interface

3. **API Endpoints**: http://127.0.0.1:8000/api/vehicles/
   - Should return empty list `[]` (no vehicles yet)

## Post-Installation Setup

### 1. Create Initial Data

**Via Admin Interface:**

1. Go to http://127.0.0.1:8000/admin/
2. Login with superuser credentials
3. Create a Vehicle:
   - Click "Vehicles" → "Add Vehicle"
   - Fill in: Registration, Make, Model, Year, Capacity
   - Status: Active
   - Click "Save"

4. Create a Route:
   - Click "Routes" → "Add Route"
   - Fill in: Name, Code (e.g., "RT17"), Description
   - Is Active: ✓
   - Click "Save"

5. Add Route Points:
   - Click "Route Points" → "Add Route Point"
   - Select Route
   - Sequence: 1
   - Name: "City Centre"
   - Latitude: -17.8292
   - Longitude: 31.0522
   - Click "Save"
   - Repeat for additional points

**Via Django Shell:**

```bash
python manage.py shell
```

```python
from fleet.models import Vehicle, Route, RoutePoint

# Create vehicle
vehicle = Vehicle.objects.create(
    registration="ABC-1234",
    make="Mercedes-Benz",
    model="Sprinter",
    year=2020,
    capacity=30,
    status="active"
)

# Create route
route = Route.objects.create(
    name="City Centre to Chitungwiza",
    code="RT17",
    description="Main route from city centre",
    is_active=True
)

# Add route points
RoutePoint.objects.create(
    route=route,
    sequence=1,
    name="City Centre",
    latitude=-17.8292,
    longitude=31.0522
)

RoutePoint.objects.create(
    route=route,
    sequence=2,
    name="Chitungwiza",
    latitude=-17.8700,
    longitude=31.0900
)
```

### 2. Test GPS Simulator

```bash
# Edit simulator/gps_simulator.py with your vehicle ID
python simulator/gps_simulator.py
```

Or test API directly:
```bash
curl -X POST http://localhost:8000/api/locations/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle": 1,
    "latitude": -17.8292,
    "longitude": 31.0522,
    "speed": 45.5,
    "ignition": true
  }'
```

## Troubleshooting

### Issue: Python not found

**Windows:**
- Use `py` instead of `python`
- Or add Python to PATH during installation

**Linux/Mac:**
- Use `python3` instead of `python`
- Install Python if not present: `sudo apt install python3 python3-pip`

### Issue: pip not found

```bash
# Windows
python -m ensurepip --upgrade

# Linux/Mac
sudo apt install python3-pip
```

### Issue: Permission denied

**Linux/Mac:**
```bash
# Use sudo (not recommended) or fix permissions
sudo pip install -r requirements.txt

# Better: Use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Database errors

```bash
# Delete and recreate database
rm db.sqlite3  # Linux/Mac
del db.sqlite3  # Windows

python manage.py migrate
```

### Issue: Port already in use

```bash
# Use different port
python manage.py runserver 8001
```

### Issue: Module not found

```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Migration errors

```bash
# Reset migrations (development only)
python manage.py migrate --run-syncdb
```

## Development vs Production

### Development Setup (Current)

- **Database**: SQLite3 (single file)
- **Server**: Django development server
- **Debug**: Enabled
- **CORS**: All origins allowed
- **Static Files**: Served by Django

### Production Setup (Future)

- **Database**: PostgreSQL
- **Server**: Gunicorn + Nginx
- **Debug**: Disabled
- **CORS**: Restricted origins
- **Static Files**: Served by Nginx or CDN
- **HTTPS**: SSL/TLS certificates

## Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database migrated (`python manage.py migrate`)
- [ ] Superuser created (`python manage.py createsuperuser`)
- [ ] Server runs without errors (`python manage.py runserver`)
- [ ] Admin interface accessible (http://127.0.0.1:8000/admin/)
- [ ] API accessible (http://127.0.0.1:8000/api/)
- [ ] Can create vehicle via admin
- [ ] Can send location via API

## Next Steps

After successful installation:

1. **Read User Guide**: [User Guide](./04_USER_GUIDE.md)
2. **Explore API**: [API Documentation](./05_API_DOCUMENTATION.md)
3. **Set up ESP32**: [IoT Integration](./07_IOT_INTEGRATION.md)
4. **Start Development**: [Development Guide](./08_DEVELOPMENT.md)

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)

---

**Document Version**: 1.0  
**Last Updated**: 2024

