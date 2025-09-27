#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>
#include "time.h" // Diperlukan untuk NTP

// --- KONFIGURASI ---
const char *ssid = "Wokwi-GUEST";
const char *password = "";
const char *mqtt_server = "broker.hivemq.com";
const char *mqtt_topic = "Informatika/IoT-E/Kelompok9/climate";

#define DHTPIN 4
#define DHTTYPE DHT22

// --- KONFIGURASI WAKTU (NTP) ---
const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 3600 * 7; // GMT+7 (WIB)
const int   daylightOffset_sec = 0;

// --- KONFIGURASI ALARM LED ---
#define LED_LOW_TEMP    12 // Pin GPIO untuk LED suhu rendah (Biru)
#define LED_NORMAL_TEMP 13 // Pin GPIO untuk LED suhu normal (Hijau)
#define LED_HIGH_TEMP   14 // Pin GPIO untuk LED suhu tinggi (Merah)

#define TEMP_THRESHOLD_LOW  45.0 // Batas bawah suhu normal
#define TEMP_THRESHOLD_HIGH 55.0 // Batas atas suhu normal
// --------------------

WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHTPIN, DHTTYPE);

// Fungsi untuk mengontrol LED
void setAlarmLED(float temperature) {
  // Matikan semua LED terlebih dahulu
  digitalWrite(LED_LOW_TEMP, LOW);
  digitalWrite(LED_NORMAL_TEMP, LOW);
  digitalWrite(LED_HIGH_TEMP, LOW);

  // Nyalakan LED yang sesuai
  if (temperature < TEMP_THRESHOLD_LOW) {
    digitalWrite(LED_LOW_TEMP, HIGH); // Suhu dingin
  } else if (temperature >= TEMP_THRESHOLD_LOW && temperature <= TEMP_THRESHOLD_HIGH) {
    digitalWrite(LED_NORMAL_TEMP, HIGH); // Suhu normal
  } else {
    digitalWrite(LED_HIGH_TEMP, HIGH); // Suhu panas
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();

  // Setup pin LED sebagai OUTPUT
  pinMode(LED_LOW_TEMP, OUTPUT);
  pinMode(LED_NORMAL_TEMP, OUTPUT);
  pinMode(LED_HIGH_TEMP, OUTPUT);

  // Koneksi WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Terhubung!");
  Serial.print("Alamat IP ESP32: ");
  Serial.println(WiFi.localIP());

  // Sinkronisasi waktu dari server NTP
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  Serial.println("Waktu sudah disinkronisasi");

  // Koneksi MQTT
  client.setServer(mqtt_server, 1883);
}

void loop() {
  if (!client.connected()) {
    Serial.print("Mencoba koneksi MQTT...");
    if (client.connect("esp32-client")) {
      Serial.println("terhubung!");
    } else {
      Serial.print("gagal, rc=");
      Serial.print(client.state());
      Serial.println(" coba lagi dalam 5 detik");
      delay(5000);
      return;
    }
  }

  client.loop();

  // Baca sensor
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Gagal membaca dari sensor DHT!");
    delay(2000);
    return;
  }

  // Ambil Timestamp 
  struct tm timeinfo;
  if(!getLocalTime(&timeinfo)){
    Serial.println("Gagal mendapatkan waktu lokal");
    return;
  }
  time_t timestamp = mktime(&timeinfo);

  // Buat data JSON
  JsonDocument doc;
  doc["ts"] = timestamp; // Tambahkan Unix timestamp
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;

  char jsonBuffer[128];
  serializeJson(doc, jsonBuffer);

  // Kirim (publish) data JSON ke broker
  client.publish(mqtt_topic, jsonBuffer);
    Serial.print("Data terkirim ke topic '");
  Serial.print(mqtt_topic);
  Serial.print("': ");
  Serial.println(jsonBuffer);

  // --- Atur Alarm LED ---
  setAlarmLED(temperature);

  delay(5000);
}