# API Documentation

## Base URL

```
http://localhost:8000/api/
```

For production, replace `localhost:8000` with your server address.

## Authentication

**Current Status**: Open access (development mode)

**Future**: Token-based authentication will be implemented for production.

## Response Format

All API responses are in JSON format.

### Success Response

```json
{
  "id": 1,
  "registration": "ABC-1234",
  "make": "Mercedes-Benz",
  "model": "Sprinter",
  "year": 2020,
  "capacity": 30,
  "status": "active"
}
```

### Error Response

```json
{
  "error": "Validation failed",
  "details": {
    "vehicle": ["This field is required."],
    "latitude": ["Invalid latitude value."]
  }
}
```

## Endpoints

### Vehicles

#### List Vehicles

```http
GET /api/vehicles/
```

**Response**: List of all vehicles

```json
[
  {
    "id": 1,
    "registration": "ABC-1234",
    "make": "Mercedes-Benz",
    "model": "Sprinter",
    "year": 2020,
    "capacity": 30,
    "status": "active",
    "last_location": {
      "latitude": -17.8292,
      "longitude": 31.0522,
      "speed": 45.5,
      "timestamp": "2024-01-15T10:30:00Z"
    },
    "is_online": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### Get Vehicle Details

```http
GET /api/vehicles/{id}/
```

**Parameters**:
- `id` (path): Vehicle ID

**Response**: Single vehicle object

#### Get Vehicle Locations

```http
GET /api/vehicles/{id}/locations/
```

**Parameters**:
- `id` (path): Vehicle ID
- `hours` (query, optional): Hours of history (default: 24)

**Example**:
```
GET /api/vehicles/1/locations/?hours=12
```

**Response**: List of location records

```json
[
  {
    "id": 1,
    "vehicle": 1,
    "vehicle_registration": "ABC-1234",
    "latitude": "-17.829200",
    "longitude": "31.052200",
    "speed": 45.5,
    "heading": 180.0,
    "timestamp": "2024-01-15T10:30:00Z",
    "battery": 12.5,
    "ignition": true
  }
]
```

#### Create Vehicle

```http
POST /api/vehicles/
```

**Request Body**:
```json
{
  "registration": "XYZ-5678",
  "make": "Toyota",
  "model": "Hiace",
  "year": 2021,
  "capacity": 25,
  "status": "active"
}
```

**Response**: Created vehicle object (201 Created)

### Locations

#### List Locations

```http
GET /api/locations/
```

**Query Parameters**:
- `vehicle` (optional): Filter by vehicle ID
- `hours` (optional): Hours of history (default: 24)

**Examples**:
```
GET /api/locations/?vehicle=1
GET /api/locations/?hours=12
GET /api/locations/?vehicle=1&hours=6
```

**Response**: List of location records

#### Get Recent Locations

```http
GET /api/locations/recent/
```

**Response**: Locations from last 5 minutes for all active vehicles

```json
[
  {
    "id": 1,
    "vehicle": 1,
    "vehicle_registration": "ABC-1234",
    "latitude": "-17.829200",
    "longitude": "31.052200",
    "speed": 45.5,
    "heading": 180.0,
    "timestamp": "2024-01-15T10:30:00Z",
    "battery": 12.5,
    "ignition": true
  }
]
```

#### Create Location (IoT Endpoint)

```http
POST /api/locations/create/
```

**Request Body**:
```json
{
  "vehicle": 1,
  "latitude": -17.8292,
  "longitude": 31.0522,
  "speed": 45.5,
  "heading": 180.0,
  "ignition": true,
  "battery": 12.5
}
```

**Required Fields**:
- `vehicle`: Vehicle ID (integer)
- `latitude`: Latitude (decimal, -90 to 90)
- `longitude`: Longitude (decimal, -180 to 180)
- `speed`: Speed in km/h (float, >= 0)
- `ignition`: Boolean

**Optional Fields**:
- `heading`: Direction in degrees (float, 0-360)
- `battery`: Battery voltage (float, >= 0)

**Response**: Created location object (201 Created)

**Example (cURL)**:
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

### Routes

#### List Routes

```http
GET /api/routes/
```

**Query Parameters**:
- `active` (optional): Filter active routes (`true`/`false`)

**Example**:
```
GET /api/routes/?active=true
```

**Response**: List of routes

```json
[
  {
    "id": 1,
    "name": "City Centre to Chitungwiza",
    "code": "RT17",
    "description": "Main route from city centre",
    "is_active": true,
    "point_count": 5,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### Get Route Details

```http
GET /api/routes/{id}/
```

**Parameters**:
- `id` (path): Route ID

**Response**: Single route object

#### Create Route

```http
POST /api/routes/
```

**Request Body**:
```json
{
  "name": "City Centre to Epworth",
  "code": "RT18",
  "description": "Route to Epworth",
  "is_active": true
}
```

**Response**: Created route object (201 Created)

### Route Points

#### List Route Points

```http
GET /api/route-points/
```

**Query Parameters**:
- `route` (optional): Filter by route ID

**Example**:
```
GET /api/route-points/?route=1
```

**Response**: List of route points

```json
[
  {
    "id": 1,
    "route": 1,
    "route_code": "RT17",
    "sequence": 1,
    "latitude": "-17.829200",
    "longitude": "31.052200",
    "name": "City Centre",
    "scheduled_time": "08:00:00"
  }
]
```

#### Get Route Point Details

```http
GET /api/route-points/{id}/
```

**Parameters**:
- `id` (path): Route point ID

**Response**: Single route point object

#### Create Route Point

```http
POST /api/route-points/
```

**Request Body**:
```json
{
  "route": 1,
  "sequence": 2,
  "latitude": -17.8400,
  "longitude": 31.0600,
  "name": "Stop 1",
  "scheduled_time": "08:15:00"
}
```

**Response**: Created route point object (201 Created)

### Trips

#### List Trips

```http
GET /api/trips/
```

**Query Parameters**:
- `status` (optional): Filter by status (`scheduled`, `in_progress`, `completed`, `cancelled`)
- `vehicle` (optional): Filter by vehicle ID
- `route` (optional): Filter by route ID

**Examples**:
```
GET /api/trips/?status=in_progress
GET /api/trips/?vehicle=1
GET /api/trips/?status=completed&vehicle=1
```

**Response**: List of trips

```json
[
  {
    "id": 1,
    "vehicle": 1,
    "vehicle_registration": "ABC-1234",
    "route": 1,
    "route_code": "RT17",
    "start_time": "2024-01-15T08:00:00Z",
    "end_time": "2024-01-15T09:30:00Z",
    "scheduled_start": "2024-01-15T08:00:00Z",
    "scheduled_end": "2024-01-15T09:30:00Z",
    "status": "completed",
    "duration_minutes": 90.0,
    "delay_minutes": 0.0,
    "created_at": "2024-01-15T07:00:00Z"
  }
]
```

#### Get Trip Details

```http
GET /api/trips/{id}/
```

**Parameters**:
- `id` (path): Trip ID

**Response**: Single trip object

#### Create Trip

```http
POST /api/trips/
```

**Request Body**:
```json
{
  "vehicle": 1,
  "route": 1,
  "scheduled_start": "2024-01-15T08:00:00Z",
  "scheduled_end": "2024-01-15T09:30:00Z",
  "status": "scheduled"
}
```

**Response**: Created trip object (201 Created)

#### Update Trip

```http
PATCH /api/trips/{id}/
```

**Request Body** (partial update):
```json
{
  "status": "in_progress",
  "start_time": "2024-01-15T08:05:00Z"
}
```

**Response**: Updated trip object (200 OK)

## HTTP Status Codes

- `200 OK`: Successful GET, PUT, PATCH request
- `201 Created`: Successful POST request
- `400 Bad Request`: Invalid input data
- `404 Not Found`: Resource doesn't exist
- `500 Internal Server Error`: Server error

## Pagination

List endpoints support pagination:

```
GET /api/vehicles/?page=1
```

**Response**:
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/vehicles/?page=2",
  "previous": null,
  "results": [...]
}
```

## Filtering and Searching

### Filtering

Use query parameters to filter results:

```
GET /api/locations/?vehicle=1&hours=12
```

### Searching

Some endpoints support search (via admin interface or custom implementation).

## Rate Limiting

**Current**: No rate limiting (development)

**Future**: Rate limiting will be implemented for production to prevent abuse.

## Error Handling

### Validation Errors

```json
{
  "vehicle": ["This field is required."],
  "latitude": ["Invalid latitude value. Must be between -90 and 90."]
}
```

### Not Found

```json
{
  "detail": "Not found."
}
```

## Examples

### Complete Workflow

1. **Create Vehicle**:
```bash
curl -X POST http://localhost:8000/api/vehicles/ \
  -H "Content-Type: application/json" \
  -d '{
    "registration": "ABC-1234",
    "make": "Mercedes-Benz",
    "model": "Sprinter",
    "year": 2020,
    "capacity": 30,
    "status": "active"
  }'
```

2. **Send Location**:
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

3. **Get Vehicle Locations**:
```bash
curl http://localhost:8000/api/vehicles/1/locations/
```

### Python Example

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000/api"

# Send location
location_data = {
    "vehicle": 1,
    "latitude": -17.8292,
    "longitude": 31.0522,
    "speed": 45.5,
    "ignition": True
}

response = requests.post(
    f"{BASE_URL}/locations/create/",
    json=location_data
)

print(response.status_code)
print(response.json())
```

### JavaScript Example

```javascript
// Send location
fetch('http://localhost:8000/api/locations/create/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    vehicle: 1,
    latitude: -17.8292,
    longitude: 31.0522,
    speed: 45.5,
    ignition: true
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## Browsable API

Django REST Framework provides a browsable API interface:

- Visit: http://localhost:8000/api/
- Navigate to endpoints
- Test API directly from browser
- View request/response formats

## Next Steps

- **User Guide**: [User Guide](./04_USER_GUIDE.md)
- **Development**: [Development Guide](./08_DEVELOPMENT.md)
- **IoT Integration**: [IoT Integration](./07_IOT_INTEGRATION.md)

---

**Document Version**: 1.0  
**Last Updated**: 2024

