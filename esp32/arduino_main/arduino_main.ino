/**
 * ESP32 Arduino Code for ZUPCO IoT Fleet Management System
 * 
 * Hardware Requirements:
 * - ESP32 Development Board
 * - NEO-6M GPS Module (or compatible)
 * - Optional: Battery voltage monitoring
 * 
 * Connections:
 * - GPS VCC -> ESP32 3.3V
 * - GPS GND -> ESP32 GND
 * - GPS TX -> ESP32 GPIO 16 (RX pin)
 * - GPS RX -> ESP32 GPIO 17 (TX pin) - Optional, for configuration
 * 
 * Required Libraries:
 * - WiFi (built-in)
 * - HTTPClient (built-in)
 * - ArduinoJson (install via Library Manager)
 * - TinyGPS++ (install via Library Manager)
 * 
 * Author: ZUPCO Research Project
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <TinyGPS++.h>
#include <HardwareSerial.h>

// ============================================================================
// CONFIGURATION - UPDATE THESE VALUES
// ============================================================================

// WiFi Configuration
const char* WIFI_SSID = "HIGHLINK-52F006";
const char* WIFI_PASSWORD = "bc52f006";

// API Configuration
const char* API_URL = "https://utracking.pythonanywhere.com/api/locations/create/";
const char* VEHICLE_REGISTRATION = "AAA35565";  // Update with your vehicle registration number (e.g., "ABC123")

// GPS Configuration
#define GPS_RX_PIN 16
#define GPS_TX_PIN 17
#define GPS_BAUDRATE 9600

// Update Interval (milliseconds)
const unsigned long UPDATE_INTERVAL = 30000;  // 30 seconds

// Battery Monitoring (Optional)
#define ENABLE_BATTERY_MONITOR false
#define BATTERY_ADC_PIN 34  // GPIO34 is ADC1_CH6 (input only)
#define BATTERY_VOLTAGE_DIVIDER 2.0  // Adjust based on your voltage divider circuit

// Status LED
#define LED_PIN 2

// ============================================================================
// GLOBAL OBJECTS
// ============================================================================

HardwareSerial gpsSerial(2);  // Use UART2
TinyGPSPlus gps;  // Class name is TinyGPSPlus (not TinyGPS++)

// ============================================================================
// SETUP
// ============================================================================

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("==================================================");
  Serial.println("ZUPCO IoT Fleet Tracker - ESP32");
  Serial.println("==================================================");
  
  // Initialize LED
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  // Initialize GPS Serial
  gpsSerial.begin(GPS_BAUDRATE, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN);
  Serial.println("GPS initialized");
  
  // Connect to WiFi
  connectWiFi();
  
  Serial.print("Vehicle Registration: ");
  Serial.println(VEHICLE_REGISTRATION);
  Serial.print("Update interval: ");
  Serial.print(UPDATE_INTERVAL / 1000);
  Serial.println(" seconds");
  Serial.println("Waiting for GPS fix...");
  Serial.println("==================================================");
}

// ============================================================================
// WIFI CONNECTION
// ============================================================================

void connectWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(WIFI_SSID);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 20) {
    delay(500);
    Serial.print(".");
    retries++;
  }
  Serial.println();
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("WiFi connected! IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("WiFi connection failed!");
    Serial.println("Restarting in 10 seconds...");
    delay(10000);
    ESP.restart();
  }
}

// ============================================================================
// BATTERY MONITORING
// ============================================================================

float readBatteryVoltage() {
  if (!ENABLE_BATTERY_MONITOR) {
    return 0.0;
  }
  
  // Read multiple samples and average
  float sum = 0;
  for (int i = 0; i < 10; i++) {
    int adcValue = analogRead(BATTERY_ADC_PIN);
    float voltage = (adcValue / 4095.0) * 3.3 * BATTERY_VOLTAGE_DIVIDER;
    sum += voltage;
    delay(10);
  }
  
  return sum / 10.0;
}

// ============================================================================
// API COMMUNICATION
// ============================================================================

bool sendLocationToAPI(float latitude, float longitude, float speed, 
                       float heading, bool ignition, float battery) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected!");
    connectWiFi();
    return false;
  }
  
  HTTPClient http;
  http.begin(API_URL);
  http.addHeader("Content-Type", "application/json");
  

  // Create JSON payload
  StaticJsonDocument<200> doc;
  doc["registration"] = VEHICLE_REGISTRATION;
  doc["latitude"] = latitude;
  doc["longitude"] = longitude;
  doc["speed"] = speed;
  doc["ignition"] = ignition;
  
  if (heading >= 0 && heading <= 360) {
    doc["heading"] = heading;
  }
  
  if (battery > 0) {
    doc["battery"] = battery;
  }
  
  String jsonPayload;
  serializeJson(doc, jsonPayload);
  
  Serial.print("Sending: ");
  Serial.println(jsonPayload);
  
  int httpResponseCode = http.POST(jsonPayload);
  
  bool success = false;
  if (httpResponseCode > 0) {
    Serial.print("Response code: ");
    Serial.println(httpResponseCode);
    
    if (httpResponseCode == 200 || httpResponseCode == 201) {
      Serial.println("✓ Location sent successfully");
      success = true;
    } else {
      Serial.print("✗ API error: ");
      Serial.println(httpResponseCode);
    }
  } else {
    Serial.print("✗ Error sending request: ");
    Serial.println(http.errorToString(httpResponseCode));
  }
  
  http.end();
  return success;
}

// ============================================================================
// MAIN LOOP
// ============================================================================

unsigned long lastSendTime = 0;
int gpsFixCount = 0;
int sendSuccessCount = 0;
int sendFailCount = 0;

void loop() {
  // Blink LED to show activity
  static unsigned long lastLedToggle = 0;
  if (millis() - lastLedToggle > 500) {
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    lastLedToggle = millis();
  }
  
  // Feed GPS data to parser
  while (gpsSerial.available() > 0) {
    if (gps.encode(gpsSerial.read())) {
      // GPS data successfully parsed
      if (gps.location.isValid()) {
        gpsFixCount++;
        
        float latitude = gps.location.lat();
        float longitude = gps.location.lng();
        float speed = gps.speed.kmph();
        float heading = gps.course.deg();
        
        Serial.println();
        Serial.print("[Fix #");
        Serial.print(gpsFixCount);
        Serial.println("] GPS Data:");
        Serial.print("  Lat: ");
        Serial.println(latitude, 6);
        Serial.print("  Lon: ");
        Serial.println(longitude, 6);
        Serial.print("  Speed: ");
        Serial.print(speed, 1);
        Serial.println(" km/h");
        if (heading >= 0) {
          Serial.print("  Heading: ");
          Serial.print(heading, 1);
          Serial.println("°");
        }
        
        // Check if it's time to send update
        unsigned long currentTime = millis();
        if (currentTime - lastSendTime >= UPDATE_INTERVAL || lastSendTime == 0) {
          // Read battery voltage
          float batteryVoltage = readBatteryVoltage();
          if (batteryVoltage > 0) {
            Serial.print("  Battery: ");
            Serial.print(batteryVoltage, 2);
            Serial.println("V");
          }
          
          // Send to API
          bool success = sendLocationToAPI(
            latitude, longitude, speed, heading, true, batteryVoltage
          );
          
          if (success) {
            sendSuccessCount++;
            lastSendTime = currentTime;
          } else {
            sendFailCount++;
          }
          
          Serial.print("Stats: Success=");
          Serial.print(sendSuccessCount);
          Serial.print(", Failed=");
          Serial.println(sendFailCount);
        }
      } else {
        // No GPS fix yet
        static unsigned long lastDotTime = 0;
        if (millis() - lastDotTime > 1000) {
          Serial.print(".");
          lastDotTime = millis();
        }
      }
    }
  }
  
  // Check WiFi connection periodically
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected! Reconnecting...");
    connectWiFi();
  }
  
  delay(100);
}
