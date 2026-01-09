# Project Overview

## Introduction

The ZUPCO IoT Fleet Management System is a comprehensive solution designed to track, monitor, and manage fleet operations for the Zimbabwe United Passenger Company (ZUPCO). This system integrates Internet of Things (IoT) technology with web-based management tools to provide real-time visibility into fleet operations.

## Research Context

This system was developed to support graduate-level research on:

**"THE IMPACT OF AN INTEGRATED IOT TRACKING AND WEB APPLICATION SYSTEM ON FLEET MANAGEMENT EFFICIENCY; CASE OF ZIMBABWE UNITED PASSENGER COMPANY (ZUPCO)."**

### Research Objectives

1. **Assess Current Practices**: Evaluate existing fleet management practices and identify inefficiencies
2. **Design System Framework**: Develop a conceptual framework for IoT-integrated fleet management
3. **Evaluate Impact**: Measure the impact on key performance indicators (KPIs):
   - Route adherence percentage
   - Schedule deviation (minutes)
   - Vehicle utilization rate
   - Fuel cost per kilometer
   - Average idling time
4. **Provide Recommendations**: Offer implementation guidance based on findings

### Theoretical Framework

The system is designed around the **Technology-Organization-Environment (TOE) Framework**, analyzing:

- **Technological Factors**: IoT/telematics capabilities, web application features
- **Organizational Factors**: ZUPCO's resources, skills, organizational structure
- **Environmental Factors**: Government policy, commuter expectations, competitive landscape

## System Purpose

The ZUPCO IoT Fleet Management System addresses critical operational challenges:

### Problems Addressed

1. **Operational Blind Spots**: Lack of real-time visibility into vehicle locations
2. **Inaccurate ETAs**: Inability to provide accurate arrival times to commuters
3. **Inefficient Routing**: No dynamic routing based on real-time conditions
4. **Poor Asset Utilization**: Limited visibility into vehicle usage patterns
5. **High Operational Costs**: Inability to optimize routes and reduce fuel consumption

### Value Proposition

- **Real-time Tracking**: GPS-based location monitoring for all vehicles
- **Route Management**: Define and monitor routes with scheduled stops
- **Performance Analytics**: Track adherence, utilization, and efficiency metrics
- **Data Integration**: Bridge operational data (IoT) with financial data (AIS) for strategic decision-making
- **Proactive Management**: Geofencing and alert systems for route deviations

## Target Users

### Primary Users

1. **Fleet Managers**: Monitor operations, analyze performance, make strategic decisions
2. **Dispatchers**: Real-time vehicle tracking, route assignment, schedule management
3. **Drivers**: (Future) Mobile app for navigation and trip information
4. **Researchers**: Data collection and analysis for research objectives

### Secondary Users

1. **Administrators**: System configuration and user management
2. **IT Support**: System maintenance and troubleshooting
3. **Executives**: High-level dashboards and reports

## System Scope

### Geographic Scope

- **Primary Focus**: Harare Metropolitan Province operations
- **Extensible**: Designed to scale to other provinces

### Functional Scope

- Vehicle tracking and monitoring
- Route definition and management
- Trip scheduling and tracking
- Performance analytics and reporting
- Data export for analysis

### Technical Scope

- **Backend**: Django 4.2+ with Django REST Framework
- **Database**: SQLite3 (development), PostgreSQL (production-ready)
- **Frontend**: Django templates with HTMX (current), React (future)
- **IoT**: ESP32 with NEO-6M GPS modules
- **Communication**: HTTP REST API

## Key Features

### Core Features

1. **Real-time Vehicle Tracking**
   - GPS location updates every 30 seconds
   - Vehicle status monitoring (active/idle/offline)
   - Historical location data

2. **Route Management**
   - Define routes with multiple stops
   - Scheduled arrival times
   - Route adherence monitoring

3. **Trip Management**
   - Schedule trips with vehicles and routes
   - Track actual vs scheduled times
   - Calculate delays and performance metrics

4. **Analytics & Reporting**
   - Route adherence percentage
   - Vehicle utilization rates
   - Average speeds and idle times
   - Performance dashboards

5. **Data Export**
   - CSV export for statistical analysis
   - API access for custom integrations
   - Historical data queries

### Research-Specific Features

1. **Simulation Mode**: Generate realistic GPS data for testing
2. **KPI Calculation**: Automated calculation of research metrics
3. **Data Collection**: Structured data storage for analysis
4. **Export Tools**: Easy export to SPSS, Excel, or other analysis tools

## System Architecture Overview

```
┌─────────────┐
│   ESP32     │  GPS Data
│  + NEO-6M   │─────────────┐
└─────────────┘             │
                            ▼
                    ┌───────────────┐
                    │  Django API   │
                    │  (REST API)   │
                    └───────┬───────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
    ┌───────────┐  ┌───────────┐  ┌───────────┐
    │  SQLite   │  │   Admin   │  │ Dashboard  │
    │ Database  │  │ Interface │  │   Views    │
    └───────────┘  └───────────┘  └───────────┘
```

## Technology Stack

### Backend
- **Framework**: Django 4.2+
- **API**: Django REST Framework
- **Database**: SQLite3 (development)
- **Server**: Gunicorn (production)

### Frontend
- **Templates**: Django templates
- **Styling**: Tailwind CSS (via CDN)
- **Maps**: Leaflet.js with OpenStreetMap
- **Dynamic Updates**: HTMX

### IoT
- **Microcontroller**: ESP32
- **GPS Module**: NEO-6M
- **Communication**: WiFi (HTTP POST)
- **Language**: MicroPython or Arduino C++

## Project Status

### ✅ Completed
- Django project structure
- Database models and migrations
- REST API endpoints
- Admin interface
- ESP32 code (MicroPython and Arduino)
- GPS simulator
- Basic documentation

### 🚧 In Progress
- Dashboard with map view
- Real-time updates
- Advanced analytics

### 📋 Planned
- Mobile app for drivers
- Advanced reporting
- Alert system
- Integration with AIS

## Research Methodology Support

The system supports mixed-methods research:

### Quantitative Data
- Route adherence metrics
- Trip time data
- Vehicle utilization statistics
- Performance KPIs

### Qualitative Data
- System usage logs
- User interaction data
- Operational patterns

### Analysis Support
- Data export for statistical analysis
- Simulation mode for hypothesis testing
- Historical data queries
- KPI calculation automation

## Success Criteria

### Technical Success
- ✅ System runs on single server/computer
- ✅ Tracks 50+ vehicles simultaneously
- ✅ Provides data for research analysis
- ✅ Easy to modify and extend
- ✅ Clear documentation

### Research Success
- Provides measurable KPIs for analysis
- Enables before/after comparison
- Supports statistical hypothesis testing
- Generates data for thesis findings

## Next Steps

1. Complete dashboard implementation
2. Deploy to test environment
3. Conduct pilot testing with ZUPCO
4. Collect baseline data
5. Implement IoT devices
6. Collect operational data
7. Analyze results for research

## Contact & Support

For questions or support:
- Review documentation in `/docs` directory
- Check troubleshooting guides
- Contact project supervisor for research-related questions

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Project**: ZUPCO IoT Fleet Management System

