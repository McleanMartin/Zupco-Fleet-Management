# User Guide

## Overview

This guide explains how to use the ZUPCO IoT Fleet Management System for day-to-day operations, data management, and monitoring.

## Table of Contents

1. [Admin Interface](#admin-interface)
2. [Vehicle Management](#vehicle-management)
3. [Route Management](#route-management)
4. [Trip Management](#trip-management)
5. [Location Tracking](#location-tracking)
6. [Using the API](#using-the-api)
7. [GPS Simulator](#gps-simulator)

## Admin Interface

### Accessing Admin

1. Navigate to: http://127.0.0.1:8000/admin/
2. Login with your superuser credentials
3. You'll see the admin dashboard

### Admin Sections

- **Fleet**: Vehicle, Location, Route, RoutePoint, Trip management
- **Authentication and Authorization**: User management (if implemented)

## Vehicle Management

### Creating a Vehicle

1. Go to **Fleet** → **Vehicles** → **Add Vehicle**
2. Fill in the form:
   - **Registration**: Vehicle registration number (e.g., "ABC-1234")
   - **Make**: Manufacturer (e.g., "Mercedes-Benz")
   - **Model**: Vehicle model (e.g., "Sprinter")
   - **Year**: Manufacturing year (e.g., 2020)
   - **Capacity**: Passenger capacity (e.g., 30)
   - **Status**: 
     - Active: Currently in service
     - In Maintenance: Under repair
     - Inactive: Not in use
3. Click **Save**

### Viewing Vehicles

- **List View**: Shows all vehicles with key information
- **Search**: Use search box to find vehicles by registration, make, or model
- **Filter**: Filter by status (Active, Maintenance, Inactive)
- **Details**: Click vehicle to see full details and related data

### Editing a Vehicle

1. Go to **Vehicles** → Click on vehicle
2. Modify fields as needed
3. Click **Save**

### Vehicle Status Indicators

- **Active**: Vehicle is operational and receiving GPS data
- **In Maintenance**: Vehicle is being serviced
- **Inactive**: Vehicle is not in use

### Vehicle Properties

- **Last Location**: Most recent GPS coordinates
- **Is Online**: Whether vehicle reported location in last 5 minutes

## Route Management

### Creating a Route

1. Go to **Fleet** → **Routes** → **Add Route**
2. Fill in:
   - **Name**: Descriptive name (e.g., "City Centre to Chitungwiza")
   - **Code**: Route code (e.g., "RT17")
   - **Description**: Additional details
   - **Is Active**: Whether route is currently in use
3. Click **Save**

### Adding Route Points (Stops)

1. Go to **Fleet** → **Route Points** → **Add Route Point**
2. Fill in:
   - **Route**: Select the route
   - **Sequence**: Order number (1, 2, 3, ...)
   - **Name**: Stop name (e.g., "City Centre")
   - **Latitude**: GPS latitude (-17.8292)
   - **Longitude**: GPS longitude (31.0522)
   - **Scheduled Time**: Optional arrival time (HH:MM:SS)
3. Click **Save**
4. Repeat for all stops in order

### Route Planning Tips

- **Sequence Matters**: Points must be in order (1, 2, 3, ...)
- **Accurate Coordinates**: Use GPS coordinates from actual locations
- **Scheduled Times**: Helpful for route adherence analysis
- **Test Routes**: Create test routes before deploying

## Trip Management

### Creating a Trip

1. Go to **Fleet** → **Trips** → **Add Trip**
2. Fill in:
   - **Vehicle**: Select vehicle
   - **Route**: Select route (optional)
   - **Scheduled Start**: Planned departure time
   - **Scheduled End**: Planned arrival time
   - **Status**: 
     - Scheduled: Not yet started
     - In Progress: Currently running
     - Completed: Finished
     - Cancelled: Cancelled trip
3. Click **Save**

### Updating Trip Status

**Starting a Trip:**
1. Open trip details
2. Set **Start Time** to current time
3. Change **Status** to "In Progress"
4. Click **Save**

**Completing a Trip:**
1. Open trip details
2. Set **End Time** to current time
3. Change **Status** to "Completed"
4. Click **Save**

### Trip Metrics

- **Duration Minutes**: Calculated from start and end times
- **Delay Minutes**: Difference between scheduled and actual start

## Location Tracking

### Viewing Recent Locations

1. Go to **Fleet** → **Locations**
2. View list of all location records
3. Filter by:
   - Vehicle (search box)
   - Ignition status
   - Date (date hierarchy)

### Location Data Fields

- **Vehicle**: Which vehicle
- **Latitude/Longitude**: GPS coordinates
- **Speed**: Speed in km/h
- **Heading**: Direction in degrees (0-360)
- **Timestamp**: When location was recorded
- **Battery**: Battery voltage (if available)
- **Ignition**: Whether vehicle is running

### Understanding Location Data

- **Recent Locations**: Locations from last 24 hours (default)
- **GPS Accuracy**: Typically 5-10 meters
- **Update Frequency**: Every 30 seconds (configurable in ESP32)

## Using the API

### API Access

- **Browsable API**: http://127.0.0.1:8000/api/
- **JSON API**: Same URLs, returns JSON

### Common API Operations

#### Get All Vehicles

```bash
curl http://localhost:8000/api/vehicles/
```

#### Get Vehicle Details

```bash
curl http://localhost:8000/api/vehicles/1/
```

#### Get Vehicle Locations

```bash
curl http://localhost:8000/api/vehicles/1/locations/
```

#### Get Recent Locations (Last 5 Minutes)

```bash
curl http://localhost:8000/api/locations/recent/
```

#### Send Location (from IoT Device)

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

### API Filtering

**Filter locations by vehicle:**
```
GET /api/locations/?vehicle=1
```

**Filter locations by time:**
```
GET /api/locations/?hours=12
```

**Filter routes (active only):**
```
GET /api/routes/?active=true
```

**Filter trips by status:**
```
GET /api/trips/?status=in_progress
```

## GPS Simulator

### Purpose

The GPS simulator generates realistic location data for testing and development without physical hardware.

### Running the Simulator

1. **Edit Configuration**:
   ```python
   # In simulator/gps_simulator.py
   vehicle_routes = {
       1: route_cc_to_chitungwiza,  # Vehicle ID 1
       2: route_cc_to_epworth,      # Vehicle ID 2
   }
   ```

2. **Run Simulator**:
   ```bash
   python simulator/gps_simulator.py
   ```

3. **Monitor Output**:
   - Console shows location updates
   - Check admin interface for new locations
   - View on map (when dashboard is implemented)

### Simulator Features

- **Multiple Vehicles**: Simulate multiple vehicles simultaneously
- **Route Following**: Vehicles follow defined routes
- **Realistic Movement**: Speed variations, GPS noise
- **Configurable**: Update interval, speed ranges

### Simulator Configuration

```python
# Update interval (seconds)
interval = 30

# Speed range (km/h)
speed_range = (20, 60)

# Loop route
loop = True
```

## Best Practices

### Data Entry

1. **Consistent Naming**: Use consistent naming conventions
2. **Accurate Coordinates**: Verify GPS coordinates before entering
3. **Complete Data**: Fill in all relevant fields
4. **Regular Updates**: Keep vehicle status current

### Route Management

1. **Test Routes**: Test routes before assigning to vehicles
2. **Verify Points**: Ensure route points are in correct order
3. **Update Schedules**: Keep scheduled times accurate
4. **Document Changes**: Note route changes and reasons

### Trip Tracking

1. **Start Promptly**: Update trip status when vehicle departs
2. **Monitor Progress**: Check locations during trip
3. **Complete Accurately**: Record actual end times
4. **Review Delays**: Analyze delay patterns

### System Monitoring

1. **Check Online Status**: Monitor which vehicles are online
2. **Review Locations**: Verify GPS data quality
3. **Track Performance**: Monitor route adherence
4. **Address Issues**: Fix problems promptly

## Common Tasks

### Task: Add New Vehicle to System

1. Create vehicle in admin
2. Note the vehicle ID
3. Configure ESP32 with vehicle ID
4. Deploy ESP32 to vehicle
5. Verify location data appears

### Task: Create New Route

1. Create route in admin
2. Add route points in sequence
3. Set scheduled times (optional)
4. Test route with simulator
5. Assign to vehicles

### Task: Monitor Vehicle in Real-Time

1. Go to Locations in admin
2. Filter by vehicle
3. Sort by timestamp (newest first)
4. Check last location time
5. Verify vehicle is online

### Task: Export Data for Analysis

1. Use API to query data
2. Save JSON response
3. Convert to CSV/Excel
4. Import to analysis tool (SPSS, Excel, etc.)

## Troubleshooting

### No Location Data

- Check ESP32 is powered and connected
- Verify WiFi connection
- Check API URL in ESP32 code
- Verify vehicle ID matches
- Check Django server is running

### Incorrect Coordinates

- Verify GPS module has clear sky view
- Wait for GPS fix (30-60 seconds)
- Check GPS module wiring
- Verify coordinate format (decimal degrees)

### Vehicle Shows Offline

- Check last location timestamp
- Verify ESP32 is sending data
- Check network connectivity
- Review ESP32 serial output

## Next Steps

- **API Documentation**: [API Documentation](./05_API_DOCUMENTATION.md)
- **Development**: [Development Guide](./08_DEVELOPMENT.md)
- **IoT Setup**: [IoT Integration](./07_IOT_INTEGRATION.md)

---

**Document Version**: 1.0  
**Last Updated**: 2024

