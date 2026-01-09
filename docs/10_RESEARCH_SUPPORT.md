# Research Support Features

## Data Collection for Research

### Key Performance Indicators (KPIs)

The system automatically calculates:

1. **Route Adherence Percentage**
   - Scheduled vs actual arrival times
   - Formula: (On-time arrivals / Total arrivals) × 100

2. **Schedule Deviation (Minutes)**
   - Difference between scheduled and actual times
   - Positive = delay, Negative = early

3. **Vehicle Utilization Rate**
   - Hours operational / Total available hours
   - Formula: (Operational time / 24 hours) × 100

4. **Average Speed**
   - Calculated from GPS speed data
   - Per trip, per route, or overall

5. **Idle Time**
   - Time vehicle is stationary
   - Calculated from speed = 0

### Data Export

#### Via API
```bash
# Export locations
curl http://localhost:8000/api/locations/?hours=168 > locations.json

# Export trips
curl http://localhost:8000/api/trips/?status=completed > trips.json
```

#### Via Django Admin
- Use admin interface to view data
- Export to CSV (future feature)

#### Via Django Shell
```python
from fleet.models import Location, Trip
import csv

# Export locations
locations = Location.objects.filter(timestamp__gte=start_date)
# Convert to CSV format
```

### Simulation Mode

The GPS simulator generates realistic data for:
- Hypothesis testing
- Before/after comparisons
- Statistical analysis

### Statistical Analysis Support

#### Data Format
- JSON format for easy import
- Timestamped data for time series analysis
- Structured for SPSS, Excel, R, Python

#### Recommended Analysis
- Paired t-tests (before/after)
- Descriptive statistics
- Regression analysis
- Time series analysis

### Research Workflow

1. **Baseline Data Collection**
   - Collect data before IoT implementation
   - Use simulation or manual logs

2. **Implementation**
   - Deploy IoT system
   - Collect operational data

3. **Analysis**
   - Export data
   - Perform statistical tests
   - Compare KPIs

4. **Reporting**
   - Document findings
   - Include in thesis

---

**Document Version**: 1.0

