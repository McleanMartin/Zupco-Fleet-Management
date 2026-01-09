# ESP32 Code for ZUPCO IoT Fleet Management

This directory contains ESP32 code for sending GPS location data to the Django API.

## 📁 Files

- **`micropython_main.py`** - MicroPython version (recommended for flexibility)
- **`arduino_main.ino`** - Arduino IDE version (easier for beginners)
- **`README.md`** - This file

## 🔧 Hardware Setup

### Required Components
- ESP32 Development Board (ESP32-WROOM-32 or similar)
- NEO-6M GPS Module (or compatible GPS module)
- Antenna for GPS module
- USB cable for programming and power
- Optional: Battery pack for mobile deployment

### Wiring Diagram

```
ESP32          NEO-6M GPS Module
------         ------------------
3.3V    -----> VCC
GND     -----> GND
GPIO 16 -----> TX (GPS TX to ESP32 RX)
GPIO 17 -----> RX (GPS RX to ESP32 TX) [Optional]
```

**Note:** The GPS module's TX pin connects to ESP32's RX pin (GPIO 16), and vice versa.

### Optional: Battery Monitoring

If you want to monitor battery voltage:
- Connect a voltage divider circuit to GPIO 34
- Adjust `BATTERY_VOLTAGE_DIVIDER` constant based on your divider ratio
- Set `ENABLE_BATTERY_MONITOR = True`

## 📝 Configuration

### Before Uploading Code

1. **WiFi Credentials**
   ```python
   WIFI_SSID = "YOUR_WIFI_SSID"
   WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
   ```

2. **API URL**
   ```python
   API_URL = "http://192.168.1.100:8000/api/locations/create/"
   ```
   Replace `192.168.1.100` with your Django server's IP address.

3. **Vehicle ID**
   ```python
   VEHICLE_ID = 1
   ```
   This should match the vehicle ID in your Django admin.

4. **Update Interval**
   ```python
   UPDATE_INTERVAL = 30  # seconds
   ```
   How often to send location updates.

## 🚀 MicroPython Setup

### 1. Install MicroPython on ESP32

1. Download MicroPython firmware for ESP32:
   - Visit: https://micropython.org/download/esp32/
   - Download latest stable release

2. Install esptool:
   ```bash
   pip install esptool
   ```

3. Flash MicroPython:
   ```bash
   esptool.py --chip esp32 --port COM3 erase_flash
   esptool.py --chip esp32 --port COM3 --baud 460800 write_flash -z 0x1000 esp32-xxxxx.bin
   ```
   Replace `COM3` with your port (Windows) or `/dev/ttyUSB0` (Linux/Mac).

### 2. Upload Code

**Option A: Using ampy**
```bash
pip install adafruit-ampy
ampy --port COM3 put micropython_main.py main.py
```

**Option B: Using Thonny IDE**
1. Install Thonny IDE
2. Open `micropython_main.py`
3. Save as `main.py` to ESP32

### 3. Install Required Packages

Connect to ESP32 and install:
```python
import upip
upip.install('micropython-urequests')
```

Or manually copy `urequests` library to ESP32.

## 🔌 Arduino IDE Setup

### 1. Install ESP32 Board Support

1. Open Arduino IDE
2. Go to File → Preferences
3. Add to Additional Board Manager URLs:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Go to Tools → Board → Boards Manager
5. Search "ESP32" and install "esp32 by Espressif Systems"

### 2. Install Required Libraries

1. Go to Sketch → Include Library → Manage Libraries
2. Install:
   - **ArduinoJson** by Benoit Blanchon
   - **TinyGPS++** by Mikal Hart

### 3. Upload Code

1. Select Board: Tools → Board → ESP32 Dev Module
2. Select Port: Tools → Port → (your COM port)
3. Open `arduino_main.ino`
4. Click Upload

## 🧪 Testing

### 1. Check Serial Monitor

Open Serial Monitor (115200 baud) to see:
- WiFi connection status
- GPS fix status
- Location data
- API response codes

### 2. Verify GPS Fix

The GPS module needs:
- Clear view of sky (for first fix)
- 30-60 seconds to acquire satellites
- LED on GPS module should blink when receiving data

### 3. Test API Connection

Check Django admin or API to see if locations are being received:
```bash
curl http://localhost:8000/api/locations/recent/
```

## 🔍 Troubleshooting

### GPS Not Getting Fix

- **Problem**: No GPS data received
- **Solutions**:
  - Ensure GPS module has clear view of sky
  - Wait 30-60 seconds for first fix
  - Check wiring (TX/RX connections)
  - Verify GPS module is powered (LED should blink)
  - Try different baud rate (4800 or 115200)

### WiFi Connection Failed

- **Problem**: Cannot connect to WiFi
- **Solutions**:
  - Verify SSID and password are correct
  - Check WiFi signal strength
  - Ensure 2.4GHz network (ESP32 doesn't support 5GHz)
  - Check router settings (MAC filtering, etc.)

### API Request Failed

- **Problem**: Location data not reaching server
- **Solutions**:
  - Verify API_URL is correct (include `http://` and port)
  - Check Django server is running
  - Verify VEHICLE_ID exists in database
  - Check firewall settings
  - Test API with curl or Postman

### Memory Issues (MicroPython)

- **Problem**: Out of memory errors
- **Solutions**:
  - Reduce update frequency
  - Disable battery monitoring if not needed
  - Use `gc.collect()` more frequently
  - Consider using Arduino version

## 📊 Expected Output

### Serial Monitor Output (MicroPython)
```
==================================================
ZUPCO IoT Fleet Tracker - ESP32
==================================================
Connecting to WiFi: YourNetwork
WiFi connected! IP: 192.168.1.50
GPS initialized
Vehicle ID: 1
Update interval: 30 seconds
Waiting for GPS fix...
==================================================
.
[Fix #1] GPS Data:
  Lat: -17.829200
  Lon: 31.052200
  Speed: 45.5 km/h
  Heading: 180.0°
Sending: {"vehicle":1,"latitude":-17.8292,"longitude":31.0522,"speed":45.5,"ignition":true}
✓ Location sent successfully (Status: 201)
Stats: Success=1, Failed=0
```

## 🔐 Security Notes

**For Production:**
- Use HTTPS instead of HTTP
- Implement authentication (API keys, tokens)
- Use secure WiFi (WPA2/WPA3)
- Consider encrypting sensitive data
- Regularly update firmware

## 📱 Mobile Deployment

For mobile deployment (vehicle-mounted):

1. **Power Supply**
   - Use 12V vehicle battery with voltage regulator
   - Or use portable battery pack (5V USB)

2. **Antenna Placement**
   - Mount GPS antenna on vehicle roof
   - Ensure clear view of sky

3. **WiFi Options**
   - Use mobile hotspot
   - Or use ESP32 with SIM800L for cellular data

## 🔄 Updates and Maintenance

- Monitor battery levels (if battery-powered)
- Check GPS fix quality regularly
- Review API response codes
- Update vehicle ID if vehicle changes
- Backup configuration settings

## 📚 Additional Resources

- [ESP32 Documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/)
- [MicroPython ESP32 Guide](https://docs.micropython.org/en/latest/esp32/quickref.html)
- [NEO-6M GPS Datasheet](https://www.u-blox.com/en/product/neo-6-series)
- [TinyGPS++ Library](https://github.com/mikalhart/TinyGPSPlus)

## 🆘 Support

For issues related to:
- **Hardware**: Check wiring and component datasheets
- **Software**: Review serial monitor output for error messages
- **API**: Test API endpoints independently with curl/Postman
- **Research**: Refer to main project documentation

