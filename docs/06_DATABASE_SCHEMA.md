# Database Schema

## Overview

The ZUPCO IoT Fleet Management System uses SQLite3 for development (single-file database) and is designed to be easily migrated to PostgreSQL for production.

## Entity Relationship Diagram

```
┌──────────────┐
│   Vehicle    │
│──────────────│
│ id (PK)      │
│ registration │◄──────────┐
│ make         │           │
│ model        │           │
│ year         │           │
│ capacity     │           │
│ status       │           │
│ created_at   │           │
│ updated_at   │           │
└──────┬───────┘           │
       │                   │
       │ 1                  │
       │                    │
       │ N                  │
┌──────▼──────────┐    ┌────┴──────────┐
│    Location     │    │     Trip      │
│─────────────────│    │───────────────│
│ id (PK)         │    │ id (PK)       │
│ vehicle_id (FK) │───►│ vehicle_id(FK)│
│ latitude        │    │ route_id (FK) │
│ longitude       │    │ start_time    │
│ speed           │    │ end_time      │
│ heading         │    │ scheduled_*   │
│ timestamp       │    │ status        │
│ battery         │    │ created_at    │
│ ignition        │    │ updated_at    │
└─────────────────┘    └──────┬───────┘
                               │
                               │ N
                               │
                               │ 1
                        ┌──────▼──────┐
                        │    Route    │
                        │─────────────│
                        │ id (PK)     │
                        │ name        │
                        │ code        │
                        │ description │
                        │ is_active   │
                        │ created_at  │
                        │ updated_at  │
                        └──────┬──────┘
                               │
                               │ 1
                               │
                               │ N
                        ┌──────▼──────────┐
                        │  RoutePoint     │
                        │─────────────────│
                        │ id (PK)         │
                        │ route_id (FK)   │
                        │ sequence        │
                        │ latitude        │
                        │ longitude       │
                        │ name            │
                        │ scheduled_time  │
                        └─────────────────┘
```

## Tables

### Vehicle

Represents a vehicle in the ZUPCO fleet.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK, Auto | Primary key |
| registration | Char(20) | Unique, Not Null | Vehicle registration number |
| make | Char(50) | Not Null | Manufacturer |
| model | Char(50) | Not Null | Vehicle model |
| year | Integer | Not Null, 1990-2030 | Manufacturing year |
| capacity | Integer | Not Null, >= 1 | Passenger capacity |
| status | Char(20) | Not Null, Choices | active/maintenance/inactive |
| created_at | DateTime | Auto | Creation timestamp |
| updated_at | DateTime | Auto | Last update timestamp |

**Indexes**:
- `registration` (unique)

**Relationships**:
- One-to-Many with `Location`
- One-to-Many with `Trip`

**Status Choices**:
- `active`: Vehicle is operational
- `maintenance`: Vehicle is being serviced
- `inactive`: Vehicle is not in use

### Location

GPS location data from IoT devices.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK, Auto | Primary key |
| vehicle_id | Integer | FK, Not Null | Reference to Vehicle |
| latitude | Decimal(9,6) | Not Null | Latitude coordinate |
| longitude | Decimal(9,6) | Not Null | Longitude coordinate |
| speed | Float | Not Null, >= 0 | Speed in km/h |
| heading | Float | Nullable, 0-360 | Direction in degrees |
| timestamp | DateTime | Auto, Indexed | When location was recorded |
| battery | Float | Nullable, >= 0 | Battery voltage |
| ignition | Boolean | Not Null, Default False | Ignition status |

**Indexes**:
- `(vehicle_id, -timestamp)` - For vehicle location queries
- `(-timestamp)` - For time-based queries

**Relationships**:
- Many-to-One with `Vehicle`

**Notes**:
- Coordinates in decimal degrees (WGS84)
- Speed in kilometers per hour
- Heading: 0° = North, 90° = East, 180° = South, 270° = West

### Route

Represents a bus route in the ZUPCO network.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK, Auto | Primary key |
| name | Char(100) | Not Null | Route name |
| code | Char(10) | Unique, Not Null | Route code (e.g., "RT17") |
| description | Text | Nullable | Route description |
| is_active | Boolean | Not Null, Default True | Whether route is active |
| created_at | DateTime | Auto | Creation timestamp |
| updated_at | DateTime | Auto | Last update timestamp |

**Indexes**:
- `code` (unique)

**Relationships**:
- One-to-Many with `RoutePoint`
- One-to-Many with `Trip`

### RoutePoint

Individual stops/points along a route.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK, Auto | Primary key |
| route_id | Integer | FK, Not Null | Reference to Route |
| sequence | Integer | Not Null, >= 1 | Order in route (1, 2, 3, ...) |
| latitude | Decimal(9,6) | Not Null | Latitude coordinate |
| longitude | Decimal(9,6) | Not Null | Longitude coordinate |
| name | Char(100) | Not Null | Stop/point name |
| scheduled_time | Time | Nullable | Scheduled arrival time |

**Indexes**:
- `(route_id, sequence)` (unique) - Ensures unique sequence per route

**Relationships**:
- Many-to-One with `Route`

**Constraints**:
- Sequence must be unique within a route
- Sequence must be >= 1

### Trip

Represents a scheduled or active trip.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK, Auto | Primary key |
| vehicle_id | Integer | FK, Not Null | Reference to Vehicle |
| route_id | Integer | FK, Nullable | Reference to Route |
| start_time | DateTime | Nullable | Actual trip start time |
| end_time | DateTime | Nullable | Actual trip end time |
| scheduled_start | DateTime | Not Null | Scheduled start time |
| scheduled_end | DateTime | Not Null | Scheduled end time |
| status | Char(20) | Not Null, Choices | Trip status |
| created_at | DateTime | Auto | Creation timestamp |
| updated_at | DateTime | Auto | Last update timestamp |

**Indexes**:
- `(vehicle_id, -scheduled_start)` - For vehicle trip queries
- `(status, -scheduled_start)` - For status-based queries

**Relationships**:
- Many-to-One with `Vehicle`
- Many-to-One with `Route`

**Status Choices**:
- `scheduled`: Trip is scheduled but not started
- `in_progress`: Trip is currently running
- `completed`: Trip has finished
- `cancelled`: Trip was cancelled

**Computed Properties**:
- `duration_minutes`: Calculated from start_time and end_time
- `delay_minutes`: Calculated from scheduled_start and start_time

## Data Types

### Decimal Precision

- **Latitude/Longitude**: Decimal(9,6)
  - Range: -90.000000 to 90.000000 (latitude)
  - Range: -180.000000 to 180.000000 (longitude)
  - Precision: 6 decimal places (~0.1 meter accuracy)

### DateTime Format

- **Format**: ISO 8601 (YYYY-MM-DDTHH:MM:SS)
- **Timezone**: UTC (stored), Africa/Harare (display)
- **Example**: `2024-01-15T10:30:00Z`

### Time Format

- **Format**: HH:MM:SS
- **Example**: `08:30:00`

## Relationships Summary

| Relationship | Type | Description |
|--------------|------|-------------|
| Vehicle → Location | One-to-Many | One vehicle has many location records |
| Vehicle → Trip | One-to-Many | One vehicle can have multiple trips |
| Route → RoutePoint | One-to-Many | One route has multiple stops |
| Route → Trip | One-to-Many | One route can have multiple trips |

## Database Migrations

### Creating Migrations

```bash
python manage.py makemigrations
```

### Applying Migrations

```bash
python manage.py migrate
```

### Migration Files

Migrations are stored in:
- `fleet/migrations/` - Fleet app migrations

## Query Examples

### Get Vehicle with Latest Location

```python
from fleet.models import Vehicle

vehicle = Vehicle.objects.get(id=1)
latest_location = vehicle.last_location
```

### Get All Locations for Vehicle (Last 24 Hours)

```python
from fleet.models import Location
from django.utils import timezone
from datetime import timedelta

since = timezone.now() - timedelta(hours=24)
locations = Location.objects.filter(
    vehicle_id=1,
    timestamp__gte=since
).order_by('-timestamp')
```

### Get Route with All Points

```python
from fleet.models import Route

route = Route.objects.prefetch_related('points').get(id=1)
points = route.points.all().order_by('sequence')
```

### Get Active Trips

```python
from fleet.models import Trip

active_trips = Trip.objects.filter(
    status='in_progress'
).select_related('vehicle', 'route')
```

## Database Maintenance

### Backup

```bash
# Simple backup
cp db.sqlite3 db_backup_$(date +%Y%m%d).sqlite3
```

### Vacuum (SQLite)

```bash
python manage.py dbshell
VACUUM;
```

### Export Data

```bash
# Export to SQL
python manage.py dumpdata fleet > fleet_data.json
```

### Import Data

```bash
# Import from JSON
python manage.py loaddata fleet_data.json
```

## Production Considerations

### Migration to PostgreSQL

1. Update `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'zupco_fleet',
        'USER': 'zupco_user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

2. Install PostgreSQL adapter:
```bash
pip install psycopg2-binary
```

3. Run migrations:
```bash
python manage.py migrate
```

### Performance Optimization

1. **Indexes**: Already added on frequently queried fields
2. **Query Optimization**: Use `select_related()` and `prefetch_related()`
3. **Connection Pooling**: Configure for production
4. **Regular Backups**: Automated backup strategy

## Data Integrity

### Constraints

- Foreign key constraints ensure referential integrity
- Unique constraints prevent duplicate registrations/codes
- Check constraints validate data ranges

### Validation

- Model-level validation in Django models
- Serializer-level validation in API
- Database-level constraints

---

**Document Version**: 1.0  
**Last Updated**: 2024

