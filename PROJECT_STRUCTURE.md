# Project Structure - ZUPCO IoT Fleet Management System

## 📁 Directory Structure

```
zupco_simple/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── db.sqlite3               # SQLite database (created after migrate)
│
├── config/                  # Django project configuration
│   ├── __init__.py
│   ├── settings.py          # Django settings (SQLite, apps, etc.)
│   ├── urls.py              # Root URL configuration
│   └── wsgi.py              # WSGI configuration for deployment
│
├── fleet/                   # Main fleet management app
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py            # Core models: Vehicle, Location, Route, RoutePoint, Trip
│   ├── admin.py             # Django admin interface configuration
│   ├── views.py             # Web views (dashboard, etc.)
│   └── urls.py              # URL routing for fleet app
│
├── api/                     # REST API app
│   ├── __init__.py
│   ├── apps.py
│   ├── serializers.py       # DRF serializers for all models
│   ├── views.py             # API ViewSets and endpoints
│   └── urls.py              # API URL routing
│
├── simulator/               # GPS data simulator
│   ├── __init__.py
│   └── gps_simulator.py     # Simulates vehicle GPS data for testing
│
├── static/                  # Static files (CSS, JS, images)
├── templates/               # Django templates
│
├── README.md                # Main documentation
├── QUICKSTART.md            # Quick setup guide
├── PROJECT_STRUCTURE.md     # This file
├── setup_check.py           # Setup verification script
└── .gitignore              # Git ignore rules
```

## 🗄️ Database Models

### Vehicle
- Registration number, make, model, year, capacity
- Status (active/maintenance/inactive)
- Properties: `last_location`, `is_online`

### Location
- GPS coordinates (latitude, longitude)
- Speed, heading, timestamp
- Battery voltage, ignition status
- Foreign key to Vehicle

### Route
- Name, code, description
- Active/inactive status

### RoutePoint
- Sequence number, coordinates
- Stop name, scheduled time
- Foreign key to Route

### Trip
- Vehicle and route assignment
- Scheduled vs actual start/end times
- Status (scheduled/in_progress/completed/cancelled)
- Properties: `duration_minutes`, `delay_minutes`

## 🔌 API Endpoints

### Vehicles
- `GET /api/vehicles/` - List all vehicles
- `GET /api/vehicles/{id}/` - Vehicle details
- `GET /api/vehicles/{id}/locations/` - Vehicle locations
- `POST /api/vehicles/` - Create vehicle (admin)

### Locations
- `GET /api/locations/` - List all locations
- `GET /api/locations/recent/` - Recent locations (last 5 min)
- `POST /api/locations/create/` - **Create location (IoT endpoint)**
- `GET /api/locations/?vehicle={id}` - Filter by vehicle
- `GET /api/locations/?hours={n}` - Filter by time

### Routes
- `GET /api/routes/` - List all routes
- `GET /api/routes/{id}/` - Route details
- `GET /api/routes/?active=true` - Active routes only

### Route Points
- `GET /api/route-points/` - List all route points
- `GET /api/route-points/?route={id}` - Filter by route

### Trips
- `GET /api/trips/` - List all trips
- `GET /api/trips/?status={status}` - Filter by status
- `GET /api/trips/?vehicle={id}` - Filter by vehicle

## 🛠️ Key Features

### ✅ Implemented
- [x] Django project structure
- [x] SQLite database configuration
- [x] Core data models
- [x] Django admin interface
- [x] REST API with DRF
- [x] GPS data endpoint for IoT devices
- [x] GPS simulator for testing
- [x] Basic documentation

### 🚧 Next Phase (To Be Implemented)
- [ ] Dashboard with map view (Leaflet.js)
- [ ] Real-time vehicle tracking display
- [ ] Route adherence calculations
- [ ] KPI dashboard (utilization, adherence %)
- [ ] Data export functionality (CSV)
- [ ] Basic authentication
- [ ] Reporting views

## 🔧 Technology Stack

- **Backend**: Django 4.2+ with Django REST Framework
- **Database**: SQLite3
- **API**: RESTful API with browsable interface
- **Admin**: Django admin (built-in)
- **Simulation**: Python script for GPS data generation

## 📊 Research Support

This system provides:
1. **Data Collection**: Real-time location tracking
2. **Route Management**: Define and track routes
3. **Trip Tracking**: Scheduled vs actual times
4. **KPI Data**: Route adherence, utilization metrics
5. **Export Ready**: Data accessible via API for analysis

## 🚀 Deployment

### Development
```bash
python manage.py runserver
```

### Simple Production
```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2
```

## 📝 Notes

- SQLite is used for simplicity (single file, no server)
- CORS is enabled for development (restrict in production)
- API permissions are open for development (add auth in production)
- Timezone is set to Africa/Harare

