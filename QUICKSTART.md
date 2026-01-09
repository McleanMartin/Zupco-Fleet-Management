# Quick Start Guide - ZUPCO Fleet Management System

## 🚀 5-Minute Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Initialize Database
```bash
python manage.py migrate
```

### Step 3: Create Admin User
```bash
python manage.py createsuperuser
```
Enter username, email, and password when prompted.

### Step 4: Start Server
```bash
python manage.py runserver
```

### Step 5: Access the System
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **API Root**: http://127.0.0.1:8000/api/
- **API Docs**: http://127.0.0.1:8000/api/ (browsable API)

## 📝 Initial Data Setup

### 1. Create Vehicles (via Admin)
1. Go to http://127.0.0.1:8000/admin/
2. Login with your superuser credentials
3. Click "Vehicles" → "Add Vehicle"
4. Fill in:
   - Registration: `ABC-1234`
   - Make: `Mercedes-Benz`
   - Model: `Sprinter`
   - Year: `2020`
   - Capacity: `30`
   - Status: `Active`

### 2. Create Routes (via Admin)
1. Click "Routes" → "Add Route"
2. Fill in:
   - Name: `City Centre to Chitungwiza`
   - Code: `RT17`
   - Description: `Main route from city centre`
   - Is Active: ✓

3. Add Route Points:
   - Click "Route Points" → "Add Route Point"
   - Select the route
   - Add points in sequence:
     - Point 1: Name `City Centre`, Lat `-17.8292`, Lon `31.0522`
     - Point 2: Name `Stop 1`, Lat `-17.8400`, Lon `31.0600`
     - Continue adding points...

### 3. Test GPS Data (via API)
```bash
# Using cURL
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

Or use the GPS Simulator:
```bash
# Edit simulator/gps_simulator.py with your vehicle IDs and routes
python simulator/gps_simulator.py
```

## 🔧 Verification

Run the setup check script:
```bash
python setup_check.py
```

## 📊 API Testing

### Get All Vehicles
```bash
curl http://localhost:8000/api/vehicles/
```

### Get Recent Locations
```bash
curl http://localhost:8000/api/locations/recent/
```

### Get Vehicle Locations
```bash
curl http://localhost:8000/api/vehicles/1/locations/
```

## 🎯 Next Steps

1. **Add Sample Data**: Use admin interface to add vehicles and routes
2. **Run GPS Simulator**: Generate test location data
3. **Build Dashboard**: Create frontend views (coming in next phase)
4. **Export Data**: Use admin or API to export data for analysis

## 🐛 Troubleshooting

### Database Errors
```bash
# Delete and recreate database
rm db.sqlite3
python manage.py migrate
```

### Import Errors
```bash
# Make sure you're in the project root directory
# Verify Python path includes the project
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Port Already in Use
```bash
# Use a different port
python manage.py runserver 8001
```

## 📚 For Research

This system supports your research by:
- **Data Collection**: Track route adherence, trip times
- **KPI Calculation**: Route adherence %, utilization rates
- **Export**: Data can be exported via admin or API for statistical analysis
- **Simulation**: Generate realistic test data for hypothesis testing

