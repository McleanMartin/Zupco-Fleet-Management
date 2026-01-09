# ZUPCO IoT Fleet Management System

A simple yet functional IoT fleet management system for ZUPCO (Zimbabwe United Passenger Company) designed to support research on the impact of integrated IoT tracking systems on fleet management efficiency.

## Features

- **Real-time Vehicle Tracking**: GPS location data from IoT devices
- **Route Management**: Define routes with stops and scheduled times
- **Trip Management**: Track scheduled and actual trip times
- **RESTful API**: Simple HTTP endpoints for IoT devices and frontend
- **Admin Interface**: Django admin for data management
- **SQLite Database**: Single-file database, no server setup required

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd zupco_simple
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (for admin access):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

7. **Access the application:**
   - Admin interface: http://127.0.0.1:8000/admin/
   - API root: http://127.0.0.1:8000/api/
   - Dashboard: http://127.0.0.1:8000/

## API Endpoints

### Vehicles
- `GET /api/vehicles/` - List all vehicles
- `GET /api/vehicles/{id}/` - Get vehicle details
- `GET /api/vehicles/{id}/locations/` - Get vehicle locations
- `POST /api/vehicles/` - Create vehicle (admin)

### Locations
- `GET /api/locations/` - List all locations
- `GET /api/locations/recent/` - Get recent locations (last 5 minutes)
- `POST /api/locations/create/` - **Create location (for IoT devices)**
- `GET /api/locations/?vehicle={id}` - Filter by vehicle
- `GET /api/locations/?hours={n}` - Filter by time range

### Routes
- `GET /api/routes/` - List all routes
- `GET /api/routes/{id}/` - Get route details
- `GET /api/routes/?active=true` - Filter active routes

### Trips
- `GET /api/trips/` - List all trips
- `GET /api/trips/?status={status}` - Filter by status
- `GET /api/trips/?vehicle={id}` - Filter by vehicle

## IoT Device Integration

### ESP32 Code

Complete ESP32 code is available in the `esp32/` directory:

- **`esp32/micropython_main.py`** - MicroPython version (recommended)
- **`esp32/arduino_main.ino`** - Arduino IDE version
- **`esp32/README.md`** - Detailed setup and configuration guide

**Quick Setup:**
1. Configure WiFi credentials and API URL in the code
2. Upload to ESP32 board
3. Connect NEO-6M GPS module (TX to GPIO 16, RX to GPIO 17)
4. Device will automatically send location data to the API

See `esp32/README.md` for complete hardware setup, wiring diagrams, and troubleshooting.

### cURL Example

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

## Database Models

- **Vehicle**: Fleet vehicles with registration, make, model, capacity
- **Location**: GPS coordinates, speed, heading, timestamp
- **Route**: Bus routes with code and description
- **RoutePoint**: Individual stops along routes
- **Trip**: Scheduled and actual trip records

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Accessing Django Shell
```bash
python manage.py shell
```

## Project Structure

```
zupco_simple/
├── manage.py
├── requirements.txt
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── fleet/
│   ├── models.py      # Core data models
│   ├── admin.py       # Admin interface
│   ├── views.py       # Web views
│   └── urls.py
├── api/
│   ├── views.py       # API endpoints
│   ├── serializers.py # Data serialization
│   └── urls.py
├── esp32/
│   ├── micropython_main.py  # ESP32 MicroPython code
│   ├── arduino_main.ino      # ESP32 Arduino code
│   └── README.md             # ESP32 setup guide
├── simulator/
│   └── gps_simulator.py      # GPS data simulator
└── db.sqlite3         # SQLite database
```

## Research Support

This system is designed to support research objectives:

1. **Data Collection**: Track route adherence, trip times, vehicle utilization
2. **KPI Calculation**: Route adherence %, average speed, idle time
3. **Export Capabilities**: Data can be exported for statistical analysis
4. **Simulation Ready**: Can be used with GPS simulators for testing

## Next Steps

- [x] Add GPS simulator script
- [x] Create ESP32 code for IoT devices
- [ ] Create dashboard with map view
- [ ] Implement route adherence calculations
- [ ] Add data export functionality
- [ ] Create reporting views

## License

This project is for research purposes.

## Documentation

Comprehensive documentation is available in the `/docs` directory:

- **[Documentation Index](docs/INDEX.md)** - Complete documentation overview
- **[Project Overview](docs/01_PROJECT_OVERVIEW.md)** - Introduction and research context
- **[Architecture](docs/02_ARCHITECTURE.md)** - System design and architecture
- **[Installation Guide](docs/03_INSTALLATION.md)** - Step-by-step setup
- **[User Guide](docs/04_USER_GUIDE.md)** - How to use the system
- **[API Documentation](docs/05_API_DOCUMENTATION.md)** - Complete API reference
- **[Database Schema](docs/06_DATABASE_SCHEMA.md)** - Data models and relationships
- **[IoT Integration](docs/07_IOT_INTEGRATION.md)** - ESP32 setup guide
- **[Development Guide](docs/08_DEVELOPMENT.md)** - Development setup
- **[Deployment Guide](docs/09_DEPLOYMENT.md)** - Production deployment
- **[Research Support](docs/10_RESEARCH_SUPPORT.md)** - Research features and data collection

## Support

For questions or issues:
- Check the [documentation](docs/INDEX.md)
- Review troubleshooting guides in relevant documentation
- Contact the project supervisor for research-related questions

