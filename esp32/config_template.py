"""
Configuration Template for ESP32 GPS Tracker

Copy this file and rename it to config.py, then update with your values.
DO NOT commit config.py to version control (it contains sensitive information).
"""

# WiFi Configuration
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

# API Configuration
API_URL = "http://192.168.1.100:8000/api/locations/create/"  # Update with your server IP
VEHICLE_REGISTRATION = "ABC123"  # Update with your vehicle registration number (e.g., "ABC123")

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

# Retry Configuration
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Debug Mode
DEBUG = True  # Set to False to reduce serial output

