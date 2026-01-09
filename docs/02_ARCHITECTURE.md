# System Architecture & Design

## Architecture Overview

The ZUPCO IoT Fleet Management System follows a **monolithic architecture** with clear separation of concerns. The system is designed for simplicity, maintainability, and research support.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                             │
├─────────────────────────────────────────────────────────────┤
│  Web Browser          │  ESP32 IoT Devices  │  Mobile App   │
│  (Django Templates)   │  (GPS Trackers)     │  (Future)     │
└───────────┬───────────┴──────────┬──────────┴──────────────┘
            │                      │
            │ HTTP/HTTPS           │ HTTP POST
            │                      │
┌───────────▼──────────────────────▼──────────────────────────┐
│                    APPLICATION LAYER                        │
├─────────────────────────────────────────────────────────────┤
│  Django Framework                                            │
│  ├── URL Routing                                             │
│  ├── View Layer (Views/ViewSets)                            │
│  ├── Serializers (Data Transformation)                      │
│  └── Middleware (CORS, Security)                            │
└───────────┬──────────────────────────────────────────────────┘
            │
┌───────────▼──────────────────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                      │
├─────────────────────────────────────────────────────────────┤
│  Fleet App          │  API App        │  Simulator          │
│  ├── Models         │  ├── Views      │  ├── GPS Sim        │
│  ├── Admin          │  ├── Serializers│  └── Data Gen      │
│  └── Views          │  └── URLs      │                     │
└───────────┬──────────────────────────────────────────────────┘
            │
┌───────────▼──────────────────────────────────────────────────┐
│                    DATA LAYER                                │
├─────────────────────────────────────────────────────────────┤
│  SQLite3 Database (Development)                              │
│  ├── Vehicle Table                                           │
│  ├── Location Table                                          │
│  ├── Route Table                                             │
│  ├── RoutePoint Table                                        │
│  └── Trip Table                                              │
└──────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Django Project Structure

```
zupco_simple/
├── config/              # Project configuration
│   ├── settings.py      # Django settings
│   ├── urls.py          # Root URL configuration
│   └── wsgi.py          # WSGI application
│
├── fleet/               # Main fleet management app
│   ├── models.py        # Data models
│   ├── admin.py         # Admin interface
│   ├── views.py         # Web views
│   └── urls.py          # App URLs
│
├── api/                 # REST API app
│   ├── views.py         # API ViewSets
│   ├── serializers.py   # Data serialization
│   └── urls.py          # API URLs
│
├── simulator/           # GPS simulator
│   └── gps_simulator.py # Simulation logic
│
└── esp32/               # IoT device code
    ├── micropython_main.py
    └── arduino_main.ino
```

### 2. Data Flow

#### GPS Data Flow
```
ESP32 Device
    │
    │ (1) Read GPS coordinates
    ▼
Parse NMEA Sentences
    │
    │ (2) Extract lat/lon/speed/heading
    ▼
Format JSON Payload
    │
    │ (3) HTTP POST
    ▼
Django API Endpoint (/api/locations/create/)
    │
    │ (4) Validate & Serialize
    ▼
Location Model
    │
    │ (5) Save to Database
    ▼
SQLite Database
```

#### Web Request Flow
```
Browser
    │
    │ (1) HTTP Request
    ▼
Django URL Router
    │
    │ (2) Route to View
    ▼
View/ViewSet
    │
    │ (3) Query Database
    ▼
Model Manager
    │
    │ (4) Return Data
    ▼
Serializer
    │
    │ (5) Format Response
    ▼
HTTP Response (JSON/HTML)
```

## Design Patterns

### 1. Model-View-Template (MVT)
- **Models**: Data structure and business logic (`fleet/models.py`)
- **Views**: Request handling (`fleet/views.py`, `api/views.py`)
- **Templates**: Presentation layer (Django templates)

### 2. RESTful API Design
- **Resources**: Vehicles, Locations, Routes, Trips
- **HTTP Methods**: GET, POST, PUT, PATCH, DELETE
- **Status Codes**: Standard HTTP status codes
- **JSON Format**: Consistent JSON response structure

### 3. Serializer Pattern
- **Input Validation**: Validate incoming data
- **Data Transformation**: Convert between Python objects and JSON
- **Nested Serialization**: Handle relationships between models

## Database Design

### Entity Relationship Diagram

```
┌──────────┐         ┌──────────┐
│ Vehicle  │────────│ Location │
└────┬─────┘         └──────────┘
     │
     │
     │
┌────▼────┐         ┌──────────┐
│  Trip   │────────│  Route   │
└─────────┘         └────┬─────┘
                          │
                          │
                    ┌─────▼──────┐
                    │ RoutePoint │
                    └────────────┘
```

### Key Relationships

1. **Vehicle → Location** (One-to-Many)
   - One vehicle has many location records
   - Location tracks GPS coordinates over time

2. **Vehicle → Trip** (One-to-Many)
   - One vehicle can have multiple trips
   - Trip represents a scheduled journey

3. **Route → RoutePoint** (One-to-Many)
   - One route has multiple stops/points
   - Points define the route path

4. **Route → Trip** (One-to-Many)
   - One route can have multiple trips
   - Different vehicles can run the same route

## API Design Principles

### RESTful Conventions

1. **Resource-Based URLs**
   - `/api/vehicles/` - Collection of vehicles
   - `/api/vehicles/{id}/` - Specific vehicle
   - `/api/vehicles/{id}/locations/` - Nested resource

2. **HTTP Methods**
   - `GET` - Retrieve data
   - `POST` - Create new resource
   - `PUT/PATCH` - Update resource
   - `DELETE` - Remove resource

3. **Status Codes**
   - `200 OK` - Successful GET/PUT/PATCH
   - `201 Created` - Successful POST
   - `400 Bad Request` - Invalid input
   - `404 Not Found` - Resource doesn't exist
   - `500 Server Error` - Internal error

### Response Format

```json
{
  "id": 1,
  "registration": "ABC-1234",
  "make": "Mercedes-Benz",
  "model": "Sprinter",
  "status": "active"
}
```

## Security Architecture

### Current Implementation (Development)

1. **CORS**: Enabled for all origins (development only)
2. **CSRF**: Django CSRF protection enabled
3. **Permissions**: Open access (development only)
4. **Authentication**: Not implemented (development)

### Production Considerations

1. **Authentication**: Token-based or session-based
2. **Authorization**: Role-based access control
3. **HTTPS**: Encrypted communication
4. **API Keys**: For IoT devices
5. **Rate Limiting**: Prevent abuse
6. **Input Validation**: Strict validation on all inputs

## Scalability Considerations

### Current Limitations

- **SQLite**: Single-file database, not ideal for high concurrency
- **Single Server**: Monolithic deployment
- **Synchronous Processing**: No background task queue

### Future Scalability Options

1. **Database**: Migrate to PostgreSQL for production
2. **Caching**: Add Redis for frequently accessed data
3. **Task Queue**: Celery for background processing
4. **Load Balancing**: Multiple Django instances
5. **CDN**: For static assets
6. **Message Queue**: MQTT for IoT devices (instead of HTTP)

## Performance Optimization

### Database Optimization

1. **Indexes**: Added on frequently queried fields
   - `Location.timestamp` (for time-based queries)
   - `Location.vehicle_id` (for vehicle-specific queries)
   - `Trip.scheduled_start` (for trip queries)

2. **Query Optimization**
   - `select_related()` for foreign keys
   - `prefetch_related()` for many-to-many
   - Pagination for large result sets

### API Optimization

1. **Pagination**: Limit result sets
2. **Filtering**: Query parameters for filtering
3. **Caching**: Cache frequently accessed data
4. **Compression**: Gzip compression for responses

## Error Handling

### API Error Responses

```json
{
  "error": "Validation failed",
  "details": {
    "vehicle": ["This field is required."],
    "latitude": ["Invalid latitude value."]
  }
}
```

### Exception Handling

- **Validation Errors**: 400 Bad Request
- **Not Found**: 404 Not Found
- **Server Errors**: 500 Internal Server Error
- **Logging**: All errors logged for debugging

## Integration Points

### 1. IoT Device Integration
- **Protocol**: HTTP POST
- **Format**: JSON
- **Endpoint**: `/api/locations/create/`
- **Authentication**: (Future) API key

### 2. External Systems (Future)
- **Accounting Information System (AIS)**: Data export/import
- **Payment Systems**: Integration for fare collection
- **SMS Gateway**: Notifications to commuters
- **Mapping Services**: Enhanced routing

## Deployment Architecture

### Development
```
Developer Machine
    │
    ├── Django Dev Server (port 8000)
    ├── SQLite Database
    └── GPS Simulator
```

### Production (Simple)
```
Server
    │
    ├── Gunicorn (WSGI Server)
    ├── Nginx (Reverse Proxy)
    ├── SQLite/PostgreSQL
    └── Static Files
```

### Production (Scalable)
```
Load Balancer
    │
    ├── Server 1 (Gunicorn + Django)
    ├── Server 2 (Gunicorn + Django)
    │
    ├── PostgreSQL (Primary)
    ├── PostgreSQL (Replica)
    │
    └── Redis (Cache)
```

## Technology Choices Rationale

### Django
- **Why**: Rapid development, built-in admin, ORM
- **Trade-off**: Monolithic, but acceptable for research project

### SQLite
- **Why**: Zero configuration, single file, perfect for development
- **Trade-off**: Limited concurrency, but sufficient for MVP

### Django REST Framework
- **Why**: Powerful API framework, browsable API, serializers
- **Trade-off**: Slight overhead, but excellent developer experience

### ESP32
- **Why**: Low cost, WiFi built-in, good community support
- **Trade-off**: Limited processing, but sufficient for GPS tracking

## Future Architecture Considerations

1. **Microservices**: Split into separate services if needed
2. **Event-Driven**: MQTT for real-time IoT communication
3. **Real-time Updates**: WebSockets for live dashboard
4. **Mobile API**: Separate API version for mobile apps
5. **Analytics Service**: Separate service for data analysis

---

**Document Version**: 1.0  
**Last Updated**: 2024

