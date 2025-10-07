// Contoh kode untuk ESP32 Node yang sudah disederhanakan
// untuk kemudahan deployment multiple nodes

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

// ========================================
// KONFIGURASI YANG HARUS DIGANTI PER NODE
// ========================================

// WiFi Settings (sama untuk semua node)
const char *ssid = "Wokwi-GUEST";
const char *password = "";

// Node Settings (GANTI UNTUK SETIAP NODE!)
const char *NODE_ID = "node_001"; // node_001, node_002, node_003, dst
const float POS_X = 25.0;         // Posisi X dalam meter (0-100)
const float POS_Y = 25.0;         // Posisi Y dalam meter (0-100)

// Hardware Settings
#define DHT_PIN 4      // Pin sensor DHT
#define DHT_TYPE DHT22 // DHT22 atau DHT11
#define LED_PIN 2      // LED indikator (built-in ESP32)

// ========================================
// KONFIGURASI SISTEM (tidak perlu diubah)
// ========================================
const char *mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;
const char *mqtt_base_topic = "Informatika/IoT-E/Kelompok9/multi_node";
const unsigned long SEND_INTERVAL = 200; // Kirim data setiap 100 ms

// ========================================
// INISIALISASI
// ========================================
DHT dht(DHT_PIN, DHT_TYPE);
WiFiClient espClient;
PubSubClient client(espClient);

String mqtt_topic;
unsigned long lastSend = 0;

// ========================================
// FORWARD DECLARATIONS
// ========================================
void connectWiFi();
void connectMQTT();
void sendSensorData();

void setup()
{
  Serial.begin(115200);
  Serial.println("\n=== ESP32 Multi-Node Sensor ===");
  printf("Node ID: %s\n", NODE_ID);
  printf("Position: (%.1f, %.1f)\n", POS_X, POS_Y);

  pinMode(LED_PIN, OUTPUT);
  dht.begin();

  // Setup topic MQTT
  mqtt_topic = String(mqtt_base_topic) + "/" + String(NODE_ID);

  // Koneksi WiFi
  connectWiFi();

  // Setup MQTT
  client.setServer(mqtt_server, mqtt_port);
  connectMQTT();

  Serial.println("Setup selesai!");
}

void loop()
{
  // Pastikan koneksi tetap aktif
  if (WiFi.status() != WL_CONNECTED)
  {
    connectWiFi();
  }

  if (!client.connected())
  {
    connectMQTT();
  }

  client.loop();

  // Kirim data sensor
  if (millis() - lastSend > SEND_INTERVAL)
  {
    sendSensorData();
    lastSend = millis();
  }
}

void connectWiFi()
{
  printf("Menghubungkan ke WiFi: %s", ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi terhubung!");
  printf("IP: %s\n", WiFi.localIP().toString().c_str());
  digitalWrite(LED_PIN, HIGH);
}

void connectMQTT()
{
  while (!client.connected())
  {
    Serial.print("Menghubungkan ke MQTT...");

    String clientId = "ESP32_" + String(NODE_ID) + "_" + String(random(0xffff), HEX);

    if (client.connect(clientId.c_str()))
    {
      Serial.println(" terhubung!");
    }
    else
    {
      printf(" gagal, rc=%d. Coba lagi dalam 5 detik\n", client.state());
      delay(5000);
    }
  }
}

void sendSensorData()
{
  // Baca sensor
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  // Validasi data
  if (isnan(temperature) || isnan(humidity))
  {
    Serial.println("Gagal membaca sensor!");
    return;
  }

  // Buat JSON
  JsonDocument doc;
  doc["node_id"] = NODE_ID;
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["pos_x"] = POS_X;
  doc["pos_y"] = POS_Y;
  doc["timestamp"] = millis() / 1000;

  String payload;
  serializeJson(doc, payload);

  // Kirim ke MQTT
  if (client.publish(mqtt_topic.c_str(), payload.c_str()))
  {
    printf("[%s] T:%.1f°C H:%.1f%% ✓\n", NODE_ID, temperature, humidity);

    // Blink LED sebagai indikator
    digitalWrite(LED_PIN, LOW);
    delay(50);
    digitalWrite(LED_PIN, HIGH);
  }
  else
  {
    Serial.println("Gagal mengirim data!");
  }
}