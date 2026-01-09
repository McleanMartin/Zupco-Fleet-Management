"""
ESP32 MicroPython Code for ZUPCO IoT Fleet Management System

Hardware Requirements:
- ESP32 Development Board
- NEO-6M GPS Module (or compatible)
- Optional: Battery voltage monitoring

Connections:
- GPS VCC -> ESP32 3.3V
- GPS GND -> ESP32 GND
- GPS TX -> ESP32 GPIO 16 (RX pin)
- GPS RX -> ESP32 GPIO 17 (TX pin) - Optional, for configuration

Author: ZUPCO Research Project
"""

import machine
import time
import network
import urequests
import ujson
from machine import UART, Pin, ADC
import gc

# ============================================================================
# CONFIGURATION - UPDATE THESE VALUES
# ============================================================================

# WiFi Configuration
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

# API Configuration
API_URL = "http://192.168.1.100:8000/api/locations/create/"  # Update with your server IP
VEHICLE_ID = 1  # Update with your vehicle ID from Django admin

# GPS Configuration
GPS_UART_NUM = 2  # UART2 on ESP32
GPS_TX_PIN = 17   # ESP32 GPIO pin connected to GPS TX
GPS_RX_PIN = 16   # ESP32 GPIO pin connected to GPS RX
GPS_BAUDRATE = 9600

# Update Interval (seconds)
UPDATE_INTERVAL = 30  # Send location every 30 seconds

# Battery Monitoring (Optional)
ENABLE_BATTERY_MONITOR = False
BATTERY_ADC_PIN = 34  # GPIO34 is ADC1_CH6 (input only)
BATTERY_VOLTAGE_DIVIDER = 2.0  # Adjust based on your voltage divider circuit

# ============================================================================
# GPS PARSING FUNCTIONS
# ============================================================================

def parse_nmea_sentence(sentence):
    """
    Parse NMEA sentence to extract GPS data.
    Supports GPRMC and GPGGA sentences.
    
    Returns: dict with lat, lon, speed, heading, timestamp, or None if invalid
    """
    if not sentence.startswith(b'$'):
        return None
    
    try:
        parts = sentence.decode('utf-8').strip().split(',')
        
        if parts[0] == '$GPRMC':
            # Recommended Minimum Specific GPS/Transit Data
            if parts[2] != 'A':  # 'A' = valid, 'V' = invalid
                return None
            
            # Extract time
            time_str = parts[1] if len(parts) > 1 else None
            
            # Extract latitude
            lat_str = parts[3] if len(parts) > 3 else None
            lat_dir = parts[4] if len(parts) > 4 else None
            if lat_str and lat_dir:
                lat_deg = float(lat_str[:2])
                lat_min = float(lat_str[2:])
                latitude = lat_deg + (lat_min / 60.0)
                if lat_dir == 'S':
                    latitude = -latitude
            else:
                latitude = None
            
            # Extract longitude
            lon_str = parts[5] if len(parts) > 5 else None
            lon_dir = parts[6] if len(parts) > 6 else None
            if lon_str and lon_dir:
                lon_deg = float(lon_str[:3])
                lon_min = float(lon_str[3:])
                longitude = lon_deg + (lon_min / 60.0)
                if lon_dir == 'W':
                    longitude = -longitude
            else:
                longitude = None
            
            # Extract speed (knots)
            speed_knots = float(parts[7]) if len(parts) > 7 and parts[7] else 0.0
            speed_kmh = speed_knots * 1.852  # Convert knots to km/h
            
            # Extract heading (degrees)
            heading = float(parts[8]) if len(parts) > 8 and parts[8] else None
            
            if latitude is not None and longitude is not None:
                return {
                    'latitude': latitude,
                    'longitude': longitude,
                    'speed': speed_kmh,
                    'heading': heading,
                    'timestamp': time_str
                }
        
        elif parts[0] == '$GPGGA':
            # Global Positioning System Fix Data
            if parts[6] == '0':  # 0 = no fix, 1 = GPS fix, 2 = DGPS fix
                return None
            
            # Extract latitude
            lat_str = parts[2] if len(parts) > 2 else None
            lat_dir = parts[3] if len(parts) > 3 else None
            if lat_str and lat_dir:
                lat_deg = float(lat_str[:2])
                lat_min = float(lat_str[2:])
                latitude = lat_deg + (lat_min / 60.0)
                if lat_dir == 'S':
                    latitude = -latitude
            else:
                latitude = None
            
            # Extract longitude
            lon_str = parts[4] if len(parts) > 4 else None
            lon_dir = parts[5] if len(parts) > 5 else None
            if lon_str and lon_dir:
                lon_deg = float(lon_str[:3])
                lon_min = float(lon_str[3:])
                longitude = lon_deg + (lon_min / 60.0)
                if lon_dir == 'W':
                    longitude = -longitude
            else:
                longitude = None
            
            if latitude is not None and longitude is not None:
                return {
                    'latitude': latitude,
                    'longitude': longitude,
                    'speed': 0.0,  # GPGGA doesn't include speed
                    'heading': None,
                    'timestamp': None
                }
    
    except (ValueError, IndexError, UnicodeDecodeError) as e:
        print(f"Error parsing NMEA: {e}")
        return None
    
    return None


def read_gps_data(gps_uart, timeout=5):
    """
    Read GPS data from UART and parse NMEA sentences.
    
    Returns: dict with GPS data or None if no valid fix
    """
    start_time = time.time()
    buffer = b''
    
    while (time.time() - start_time) < timeout:
        if gps_uart.any():
            buffer += gps_uart.read()
            
            # Look for complete NMEA sentences
            while b'\r\n' in buffer:
                line, buffer = buffer.split(b'\r\n', 1)
                
                if line.startswith(b'$GP'):
                    gps_data = parse_nmea_sentence(line)
                    if gps_data:
                        return gps_data
        
        time.sleep(0.1)
    
    return None


# ============================================================================
# WIFI CONNECTION
# ============================================================================

def connect_wifi(ssid, password, max_retries=10):
    """
    Connect ESP32 to WiFi network.
    
    Returns: True if connected, False otherwise
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print(f"Connecting to WiFi: {ssid}")
        wlan.connect(ssid, password)
        
        retries = 0
        while not wlan.isconnected() and retries < max_retries:
            time.sleep(1)
            retries += 1
            print(".", end="")
        
        print()
    
    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        print(f"WiFi connected! IP: {ip}")
        return True
    else:
        print("WiFi connection failed!")
        return False


# ============================================================================
# BATTERY MONITORING
# ============================================================================

def read_battery_voltage():
    """
    Read battery voltage from ADC.
    
    Returns: Voltage in volts or None if disabled
    """
    if not ENABLE_BATTERY_MONITOR:
        return None
    
    try:
        adc = ADC(Pin(BATTERY_ADC_PIN))
        adc.atten(ADC.ATTN_11DB)  # 0-3.3V range
        
        # Read multiple samples and average
        samples = []
        for _ in range(10):
            samples.append(adc.read())
            time.sleep(0.01)
        
        avg_value = sum(samples) / len(samples)
        
        # Convert ADC value to voltage
        # ESP32 ADC is 12-bit (0-4095) for 0-3.3V
        voltage = (avg_value / 4095.0) * 3.3 * BATTERY_VOLTAGE_DIVIDER
        
        return voltage
    except Exception as e:
        print(f"Error reading battery: {e}")
        return None


# ============================================================================
# API COMMUNICATION
# ============================================================================

def send_location_to_api(vehicle_id, latitude, longitude, speed, heading=None, 
                         ignition=True, battery=None):
    """
    Send location data to Django API.
    
    Returns: True if successful, False otherwise
    """
    data = {
        'vehicle': vehicle_id,
        'latitude': float(latitude),
        'longitude': float(longitude),
        'speed': float(speed),
        'ignition': ignition
    }
    
    if heading is not None:
        data['heading'] = float(heading)
    
    if battery is not None:
        data['battery'] = float(battery)
    
    try:
        json_data = ujson.dumps(data)
        headers = {'Content-Type': 'application/json'}
        
        print(f"Sending: {json_data}")
        
        response = urequests.post(API_URL, data=json_data, headers=headers, timeout=10)
        
        status_code = response.status_code
        response.close()
        
        if status_code in [200, 201]:
            print(f"✓ Location sent successfully (Status: {status_code})")
            return True
        else:
            print(f"✗ API error: Status {status_code}")
            return False
    
    except Exception as e:
        print(f"✗ Error sending location: {e}")
        return False


# ============================================================================
# MAIN LOOP
# ============================================================================

def main():
    """Main program loop."""
    print("=" * 50)
    print("ZUPCO IoT Fleet Tracker - ESP32")
    print("=" * 50)
    
    # Connect to WiFi
    if not connect_wifi(WIFI_SSID, WIFI_PASSWORD):
        print("Failed to connect to WiFi. Restarting in 10 seconds...")
        time.sleep(10)
        machine.reset()
    
    # Initialize GPS UART
    print("Initializing GPS...")
    gps_uart = UART(GPS_UART_NUM, baudrate=GPS_BAUDRATE, 
                    tx=GPS_TX_PIN, rx=GPS_RX_PIN, timeout=1000)
    
    # Initialize battery monitoring (if enabled)
    battery_adc = None
    if ENABLE_BATTERY_MONITOR:
        battery_adc = ADC(Pin(BATTERY_ADC_PIN))
        battery_adc.atten(ADC.ATTN_11DB)
        print("Battery monitoring enabled")
    
    # Status LED (optional - connect LED to GPIO 2)
    led = Pin(2, Pin.OUT)
    
    last_send_time = 0
    gps_fix_count = 0
    send_success_count = 0
    send_fail_count = 0
    
    print(f"Vehicle ID: {VEHICLE_ID}")
    print(f"Update interval: {UPDATE_INTERVAL} seconds")
    print("Waiting for GPS fix...")
    print("=" * 50)
    
    while True:
        try:
            # Blink LED to show activity
            led.value(not led.value())
            
            # Read GPS data
            gps_data = read_gps_data(gps_uart, timeout=2)
            
            current_time = time.time()
            
            if gps_data:
                gps_fix_count += 1
                print(f"\n[Fix #{gps_fix_count}] GPS Data:")
                print(f"  Lat: {gps_data['latitude']:.6f}")
                print(f"  Lon: {gps_data['longitude']:.6f}")
                print(f"  Speed: {gps_data['speed']:.1f} km/h")
                if gps_data['heading']:
                    print(f"  Heading: {gps_data['heading']:.1f}°")
                
                # Check if it's time to send update
                if (current_time - last_send_time) >= UPDATE_INTERVAL:
                    # Read battery voltage
                    battery_voltage = read_battery_voltage()
                    if battery_voltage:
                        print(f"  Battery: {battery_voltage:.2f}V")
                    
                    # Send to API
                    success = send_location_to_api(
                        vehicle_id=VEHICLE_ID,
                        latitude=gps_data['latitude'],
                        longitude=gps_data['longitude'],
                        speed=gps_data['speed'],
                        heading=gps_data.get('heading'),
                        ignition=True,
                        battery=battery_voltage
                    )
                    
                    if success:
                        send_success_count += 1
                        last_send_time = current_time
                    else:
                        send_fail_count += 1
                    
                    print(f"Stats: Success={send_success_count}, Failed={send_fail_count}")
            else:
                print(".", end="")  # Show waiting for fix
            
            # Free memory
            gc.collect()
            
            time.sleep(1)
        
        except KeyboardInterrupt:
            print("\nStopped by user")
            break
        except Exception as e:
            print(f"\nError in main loop: {e}")
            time.sleep(5)


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fatal error: {e}")
        print("Restarting in 10 seconds...")
        time.sleep(10)
        machine.reset()

