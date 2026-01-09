# IoT Integration Guide

## Overview

This guide covers integrating ESP32-based GPS trackers with the ZUPCO Fleet Management System. The system uses ESP32 microcontrollers with NEO-6M GPS modules to send real-time location data to the Django API.

## Hardware Requirements

### Required Components

1. **ESP32 Development Board**
   - ESP32-WROOM-32 or compatible
   - Built-in WiFi
   - USB for programming

2. **NEO-6M GPS Module**
   - UART interface
   - External antenna recommended
   - 3.3V operation

3. **Power Supply**
   - USB cable (development)
   - 5V power adapter or vehicle battery (deployment)

4. **Optional Components**
   - Battery voltage divider circuit
   - Status LED
   - Enclosure for protection

### Wiring Diagram

```
ESP32                    NEO-6M GPS Module
─────────────────        ─────────────────
3.3V        ────────────► VCC
GND         ────────────► GND
GPIO 16     ────────────► TX (GPS TX → ESP32 RX)
GPIO 17     ────────────► RX (GPS RX → ESP32 TX) [Optional]
```

**Note**: The GPS module's TX pin connects to ESP32's RX pin (GPIO 16).

## Software Setup

### Option 1: MicroPython (Recommended)

#### Step 1: Install MicroPython

1. Download MicroPython firmware:
   - Visit: https://micropython.org/download/esp32/
   - Download latest stable release

2. Install esptool:
   ```bash
   pip install esptool
   ```

3. Flash MicroPython:
   ```bash
   # Erase flash
   esptool.py --chip esp32 --port COM3 erase_flash
   
   # Flash firmware
   esptool.py --chip esp32 --port COM3 --baud 460800 \
     write_flash -z 0x1000 esp32-xxxxx.bin
   ```
   Replace `COM3` with your port (Windows) or `/dev/ttyUSB0` (Linux/Mac).

#### Step 2: Upload Code

**Using Thonny IDE:**
1. Install Thonny: https://thonny.org/
2. Open `esp32/micropython_main.py`
3. Save as `main.py` to ESP32

**Using ampy:**
```bash
pip install adafruit-ampy
ampy --port COM3 put esp32/micropython_main.py main.py
```

#### Step 3: Install Dependencies

Connect to ESP32 and install:
```python
import upip
upip.install('micropython-urequests')
```

Or manually copy `urequests` library.

#### Step 4: Configure Settings

Edit `main.py` and update:
```python
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
API_URL = "http://192.168.1.100:8000/api/locations/create/"
VEHICLE_ID = 1  # Match vehicle ID in Django
```

### Option 2: Arduino IDE

#### Step 1: Install ESP32 Board Support

1. Open Arduino IDE
2. File → Preferences
3. Add to Additional Board Manager URLs:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Tools → Board → Boards Manager
5. Search "ESP32" and install

#### Step 2: Install Libraries

1. Sketch → Include Library → Manage Libraries
2. Install:
   - **ArduinoJson** by Benoit Blanchon
   - **TinyGPS++** by Mikal Hart

#### Step 3: Upload Code

1. Open `esp32/arduino_main.ino`
2. Select Board: Tools → Board → ESP32 Dev Module
3. Select Port: Tools → Port → (your COM port)
4. Configure settings in code
5. Click Upload

## Configuration

### WiFi Settings

```python
WIFI_SSID = "YourNetworkName"
WIFI_PASSWORD = "YourPassword"
```

**Requirements**:
- 2.4GHz network (ESP32 doesn't support 5GHz)
- WiFi signal strength sufficient for connection
- No MAC address filtering

### API Configuration

```python
API_URL = "http://192.168.1.100:8000/api/locations/create/"
```

**Important**:
- Replace IP address with your Django server IP
- Include `http://` prefix
- Include port number if not 80
- For production, use HTTPS

### Vehicle ID

```python
VEHICLE_ID = 1
```

**How to find Vehicle ID**:
1. Go to Django admin: http://localhost:8000/admin/
2. Navigate to Vehicles
3. Note the ID of your vehicle
4. Update ESP32 code with this ID

### Update Interval

```python
UPDATE_INTERVAL = 30  # seconds
```

**Recommendations**:
- 30 seconds: Good balance of data and battery
- 60 seconds: Better battery life
- 15 seconds: More frequent updates (higher battery usage)

## Testing

### Step 1: Serial Monitor

Open serial monitor to view output:
- **Baud Rate**: 115200
- **Line Ending**: Both NL & CR

### Step 2: Verify GPS Fix

**Indicators**:
- GPS module LED blinks when receiving satellite data
- Serial monitor shows GPS coordinates
- Wait 30-60 seconds for first fix

**Troubleshooting**:
- Ensure clear view of sky
- Wait for GPS fix (can take 1-2 minutes first time)
- Check wiring (TX/RX connections)

### Step 3: Verify WiFi Connection

**Expected Output**:
```
Connecting to WiFi: YourNetwork
WiFi connected! IP: 192.168.1.50
```

**Troubleshooting**:
- Verify SSID and password
- Check WiFi signal strength
- Ensure 2.4GHz network

### Step 4: Verify API Communication

**Expected Output**:
```
[Fix #1] GPS Data:
  Lat: -17.829200
  Lon: 31.0522
  Speed: 45.5 km/h
Sending: {"vehicle":1,"latitude":-17.8292,...}
✓ Location sent successfully (Status: 201)
```

**Verify in Django**:
1. Go to Admin → Locations
2. Check for new location records
3. Verify vehicle ID matches

## Deployment

### Vehicle Installation

1. **Mount GPS Antenna**:
   - Place on vehicle roof
   - Ensure clear view of sky
   - Secure mounting

2. **Install ESP32**:
   - Secure enclosure
   - Connect to vehicle power (12V with regulator)
   - Or use portable battery pack

3. **Power Supply**:
   - **Option A**: Vehicle battery (12V → 5V regulator → USB)
   - **Option B**: Portable battery pack (5V USB)
   - **Option C**: Dedicated power supply

4. **Network**:
   - **Option A**: Mobile hotspot
   - **Option B**: Vehicle WiFi router
   - **Option C**: SIM800L module for cellular (future)

### Testing in Vehicle

1. Power on ESP32
2. Wait for GPS fix (1-2 minutes)
3. Verify WiFi connection
4. Check serial monitor for location updates
5. Verify data appears in Django admin

## Troubleshooting

### GPS Not Getting Fix

**Symptoms**:
- No GPS coordinates in serial output
- GPS module LED not blinking

**Solutions**:
- Ensure clear view of sky
- Wait 30-60 seconds for first fix
- Check GPS module wiring
- Verify GPS module is powered
- Try different location (outdoors)

### WiFi Connection Failed

**Symptoms**:
- "WiFi connection failed!" message
- No IP address assigned

**Solutions**:
- Verify SSID and password are correct
- Check WiFi signal strength
- Ensure 2.4GHz network (not 5GHz)
- Check router settings (MAC filtering, etc.)
- Try different WiFi network

### API Request Failed

**Symptoms**:
- "API error" or "Error sending location"
- Status code not 200/201

**Solutions**:
- Verify API_URL is correct
- Check Django server is running
- Verify VEHICLE_ID exists in database
- Check firewall settings
- Test API with curl/Postman
- Check network connectivity

### Incorrect Coordinates

**Symptoms**:
- Coordinates don't match actual location
- Coordinates are 0,0 or invalid

**Solutions**:
- Wait for GPS fix (not just satellite lock)
- Verify GPS module has clear sky view
- Check GPS module is functioning
- Review NMEA sentence parsing

### Memory Issues (MicroPython)

**Symptoms**:
- Out of memory errors
- System crashes

**Solutions**:
- Reduce update frequency
- Disable battery monitoring if not needed
- Use `gc.collect()` more frequently
- Consider Arduino version

## Advanced Configuration

### Battery Monitoring

1. **Hardware Setup**:
   - Create voltage divider circuit
   - Connect to GPIO 34 (ADC input)

2. **Code Configuration**:
   ```python
   ENABLE_BATTERY_MONITOR = True
   BATTERY_ADC_PIN = 34
   BATTERY_VOLTAGE_DIVIDER = 2.0  # Adjust based on circuit
   ```

### Custom Update Interval

```python
UPDATE_INTERVAL = 60  # Change to desired seconds
```

### Retry Logic

Code includes automatic retry on failure:
- WiFi reconnection
- API request retry
- GPS data retry

## Security Considerations

### Current Implementation (Development)

- HTTP communication (not HTTPS)
- No authentication
- Open API access

### Production Recommendations

1. **HTTPS**: Use SSL/TLS certificates
2. **API Keys**: Implement API key authentication
3. **Encryption**: Encrypt sensitive data
4. **Network Security**: Use VPN or secure network
5. **Firmware Updates**: Secure update mechanism

## Maintenance

### Regular Checks

1. **GPS Accuracy**: Verify coordinates are accurate
2. **Battery Levels**: Monitor if battery monitoring enabled
3. **Network Connectivity**: Check WiFi connection stability
4. **Data Quality**: Review location data in admin
5. **Firmware Updates**: Update ESP32 firmware as needed

### Logs and Monitoring

- Serial monitor output
- Django admin location records
- API response codes
- Error messages

## Performance Optimization

### Reduce Power Consumption

1. Increase update interval
2. Disable unnecessary features
3. Use deep sleep mode (future)
4. Optimize WiFi connection

### Improve GPS Accuracy

1. Better antenna placement
2. Wait for multiple satellites
3. Use GPS + GLONASS modules
4. Implement GPS filtering

## Next Steps

- **API Documentation**: [API Documentation](./05_API_DOCUMENTATION.md)
- **User Guide**: [User Guide](./04_USER_GUIDE.md)
- **Development**: [Development Guide](./08_DEVELOPMENT.md)

## Additional Resources

- [ESP32 Documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/)
- [MicroPython ESP32 Guide](https://docs.micropython.org/en/latest/esp32/quickref.html)
- [NEO-6M GPS Datasheet](https://www.u-blox.com/en/product/neo-6-series)
- [TinyGPS++ Library](https://github.com/mikalhart/TinyGPSPlus)

---

**Document Version**: 1.0  
**Last Updated**: 2024

