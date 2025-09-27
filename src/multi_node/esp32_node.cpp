#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <time.h>

// === KONFIGURASI WIFI ===
const char *ssid = "Wokwi-GUEST";   // Ganti dengan SSID WiFi Anda
const char *password = "";          // Ganti dengan password WiFi Anda

// === KONFIGURASI MQTT ===
const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;
const char* mqtt_base_topic = "Informatika/IoT-E/Kelompok9/multi_node";

// === KONFIGURASI NODE ===
const char* NODE_ID = "node_001";         // ID unik untuk node ini
const float POS_X = 25.0;                 // Posisi X dalam meter
const float POS_Y = 25.0;                 // Posisi Y dalam meter

// === KONFIGURASI SENSOR DHT ===
#define DHT_PIN 4                          // Pin data DHT22/DHT11
#define DHT_TYPE DHT22                     // DHT22 atau DHT11
DHT dht(DHT_PIN, DHT_TYPE);

// === KONFIGURASI TIMING ===
const unsigned long SENSOR_INTERVAL = 2000;    // Interval baca sensor (ms)
const unsigned long MQTT_INTERVAL = 5000;      // Interval kirim data (ms)
const unsigned long WIFI_TIMEOUT = 10000;      // Timeout koneksi WiFi (ms)
const unsigned long MQTT_TIMEOUT = 5000;       // Timeout koneksi MQTT (ms)

// === LED STATUS (Optional) ===
#define LED_WIFI_PIN 2                     // LED indikator WiFi (built-in ESP32)
#define LED_MQTT_PIN 12                    // LED indikator MQTT (external)

// === VARIABEL GLOBAL ===
WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastSensorRead = 0;
unsigned long lastMqttSend = 0;
unsigned long lastWifiCheck = 0;

float temperature = 0.0;
float humidity = 0.0;
bool sensorReady = false;

String mqtt_topic;
String client_id;

// === STRUKTUR DATA ===
struct SensorData {
  String node_id;
  float temperature;
  float humidity;
  float pos_x;
  float pos_y;
  unsigned long timestamp;
};

void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println("=== ESP32 Multi-Node Temperature Monitor ===");
  Serial.printf("Node ID: %s\n", NODE_ID);
  Serial.printf("Position: (%.1f, %.1f)\n", POS_X, POS_Y);
  Serial.println("==========================================");
  
  // Setup LED pins
  pinMode(LED_WIFI_PIN, OUTPUT);
  pinMode(LED_MQTT_PIN, OUTPUT);
  digitalWrite(LED_WIFI_PIN, LOW);
  digitalWrite(LED_MQTT_PIN, LOW);
  
  // Inisialisasi DHT sensor
  dht.begin();
  Serial.println("DHT sensor initialized");
  
  // Generate unique client ID dan topic
  client_id = String("esp32_") + String(NODE_ID) + "_" + String(random(0xffff), HEX);
  mqtt_topic = String(mqtt_base_topic) + "/" + String(NODE_ID);
  
  Serial.printf("MQTT Client ID: %s\n", client_id.c_str());
  Serial.printf("MQTT Topic: %s\n", mqtt_topic.c_str());
  
  // Setup WiFi
  setupWiFi();
  
  // Setup MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(mqttCallback);
  
  // Setup NTP untuk timestamp
  configTime(0, 0, "pool.ntp.org", "time.nist.gov");
  
  Serial.println("Setup completed!");
}

void loop() {
  unsigned long currentTime = millis();
  
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    digitalWrite(LED_WIFI_PIN, LOW);
    Serial.println("WiFi disconnected, reconnecting...");
    setupWiFi();
  } else {
    digitalWrite(LED_WIFI_PIN, HIGH);
  }
  
  // Check MQTT connection
  if (!client.connected()) {
    digitalWrite(LED_MQTT_PIN, LOW);
    reconnectMQTT();
  } else {
    digitalWrite(LED_MQTT_PIN, HIGH);
  }
  
  client.loop();
  
  // Baca sensor secara berkala
  if (currentTime - lastSensorRead >= SENSOR_INTERVAL) {
    readSensor();
    lastSensorRead = currentTime;
  }
  
  // Kirim data via MQTT secara berkala
  if (sensorReady && (currentTime - lastMqttSend >= MQTT_INTERVAL)) {
    if (client.connected()) {
      sendSensorData();
      lastMqttSend = currentTime;
    }
  }
  
  delay(100); // Small delay untuk stability
}

void setupWiFi() {
  digitalWrite(LED_WIFI_PIN, LOW);
  Serial.printf("Connecting to WiFi: %s", ssid);
  
  WiFi.begin(ssid, password);
  
  unsigned long startTime = millis();
  while (WiFi.status() != WL_CONNECTED) {
    if (millis() - startTime > WIFI_TIMEOUT) {
      Serial.println("\nWiFi connection timeout!");
      ESP.restart(); // Restart jika gagal connect
    }
    
    delay(500);
    Serial.print(".");
  }
  
  Serial.println();
  Serial.println("WiFi connected successfully!");
  Serial.printf("IP address: %s\n", WiFi.localIP().toString().c_str());
  Serial.printf("Signal strength: %d dBm\n", WiFi.RSSI());
  
  digitalWrite(LED_WIFI_PIN, HIGH);
}

void reconnectMQTT() {
  static unsigned long lastAttempt = 0;
  unsigned long currentTime = millis();
  
  // Coba reconnect setiap 5 detik
  if (currentTime - lastAttempt < 5000) {
    return;
  }
  
  lastAttempt = currentTime;
  
  Serial.printf("Attempting MQTT connection to %s:%d...", mqtt_server, mqtt_port);
  
  if (client.connect(client_id.c_str())) {
    Serial.println(" connected!");
    
    // Optional: Subscribe ke topik kontrol
    String control_topic = mqtt_topic + "/control";
    client.subscribe(control_topic.c_str());
    
    digitalWrite(LED_MQTT_PIN, HIGH);
    
    // Kirim pesan online
    sendStatusMessage("online");
    
  } else {
    Serial.printf(" failed, rc=%d. Retry in 5 seconds\n", client.state());
    digitalWrite(LED_MQTT_PIN, LOW);
  }
}

void readSensor() {
  // Baca sensor DHT
  float newTemp = dht.readTemperature();
  float newHum = dht.readHumidity();
  
  // Validasi pembacaan sensor
  if (isnan(newTemp) || isnan(newHum)) {
    Serial.println("Failed to read from DHT sensor!");
    sensorReady = false;
    return;
  }
  
  // Filter perubahan drastis (noise reduction)
  if (sensorReady) {
    float tempDiff = abs(newTemp - temperature);
    float humDiff = abs(newHum - humidity);
    
    // Jika perubahan terlalu drastis, abaikan pembacaan
    if (tempDiff > 10.0 || humDiff > 20.0) {
      Serial.printf("Sensor reading filtered - T:%.1f->%.1f, H:%.1f->%.1f\n", 
                   temperature, newTemp, humidity, newHum);
      return;
    }
  }
  
  temperature = newTemp;
  humidity = newHum;
  sensorReady = true;
  
  Serial.printf("Sensor: T=%.1f°C, H=%.1f%%\n", temperature, humidity);
}

void sendSensorData() {
  // Buat struktur data
  SensorData data;
  data.node_id = String(NODE_ID);
  data.temperature = temperature;
  data.humidity = humidity;
  data.pos_x = POS_X;
  data.pos_y = POS_Y;
  data.timestamp = getUnixTimestamp();
  
  // Buat JSON payload
  StaticJsonDocument<200> doc;
  doc["node_id"] = data.node_id;
  doc["temperature"] = data.temperature;
  doc["humidity"] = data.humidity;
  doc["pos_x"] = data.pos_x;
  doc["pos_y"] = data.pos_y;
  doc["timestamp"] = data.timestamp;
  
  String payload;
  serializeJson(doc, payload);
  
  // Publish ke MQTT
  if (client.publish(mqtt_topic.c_str(), payload.c_str())) {
    Serial.printf("Data sent: %s\n", payload.c_str());
  } else {
    Serial.println("Failed to send data!");
  }
}

void sendStatusMessage(const char* status) {
  StaticJsonDocument<100> doc;
  doc["node_id"] = String(NODE_ID);
  doc["status"] = status;
  doc["timestamp"] = getUnixTimestamp();
  doc["uptime"] = millis() / 1000;
  
  String payload;
  serializeJson(doc, payload);
  
  String status_topic = mqtt_topic + "/status";
  client.publish(status_topic.c_str(), payload.c_str());
  
  Serial.printf("Status sent: %s\n", status);
}

unsigned long getUnixTimestamp() {
  time_t now;
  time(&now);
  return now;
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  // Handle pesan kontrol dari dashboard (optional)
  String message;
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  
  Serial.printf("Message received [%s]: %s\n", topic, message.c_str());
  
  // Parse JSON command
  StaticJsonDocument<100> doc;
  DeserializationError error = deserializeJson(doc, message);
  
  if (!error) {
    if (doc.containsKey("command")) {
      String command = doc["command"];
      
      if (command == "restart") {
        Serial.println("Restart command received");
        ESP.restart();
      } else if (command == "status") {
        sendStatusMessage("online");
      }
    }
  }
}

// === FUNGSI UTILITAS ===

void printSystemInfo() {
  Serial.println("\n=== System Information ===");
  Serial.printf("Node ID: %s\n", NODE_ID);
  Serial.printf("Position: (%.1f, %.1f)\n", POS_X, POS_Y);
  Serial.printf("WiFi SSID: %s\n", WiFi.SSID().c_str());
  Serial.printf("IP Address: %s\n", WiFi.localIP().toString().c_str());
  Serial.printf("Signal Strength: %d dBm\n", WiFi.RSSI());
  Serial.printf("MQTT Server: %s:%d\n", mqtt_server, mqtt_port);
  Serial.printf("MQTT Topic: %s\n", mqtt_topic.c_str());
  Serial.printf("Uptime: %lu seconds\n", millis() / 1000);
  Serial.printf("Free Heap: %u bytes\n", ESP.getFreeHeap());
  Serial.println("========================\n");
}

void handleSerialCommands() {
  // Handle perintah dari Serial Monitor (untuk debugging)
  if (Serial.available()) {
    String command = Serial.readString();
    command.trim();
    
    if (command == "info") {
      printSystemInfo();
    } else if (command == "restart") {
      Serial.println("Restarting ESP32...");
      ESP.restart();
    } else if (command == "test") {
      Serial.println("Sending test data...");
      sendSensorData();
    } else if (command == "status") {
      sendStatusMessage("manual_status");
    } else {
      Serial.println("Available commands: info, restart, test, status");
    }
  }
}