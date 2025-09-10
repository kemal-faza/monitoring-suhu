#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// --- KONFIGURASI ---
const char *ssid = "Wokwi-GUEST";
const char *password = "";
const char *mqtt_server = "broker.hivemq.com"; // Cth: "192.168.1.10"
const char *mqtt_topic = "0013/climate";

#define DHTPIN 4
#define DHTTYPE DHT22
// --------------------

WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHTPIN, DHTTYPE);

void setup()
{
  Serial.begin(115200);
  dht.begin();

  // Koneksi WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Terhubung!");
  Serial.print("Alamat IP ESP32: ");
  Serial.println(WiFi.localIP());

  // Koneksi MQTT
  client.setServer(mqtt_server, 1883);
}

void loop()
{
  // Pastikan koneksi MQTT tetap terhubung
  if (!client.connected())
  {
    Serial.print("Mencoba koneksi MQTT...");
    if (client.connect("esp32-client"))
    {
      Serial.println("terhubung!");
    }
    else
    {
      Serial.print("gagal, rc=");
      Serial.print(client.state());
      Serial.println(" coba lagi dalam 5 detik");
      delay(5000);
      return;
    }
  }

  client.loop(); // Wajib ada untuk menjaga koneksi

  // Baca sensor
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  if (isnan(humidity) || isnan(temperature))
  {
    Serial.println("Gagal membaca dari sensor DHT!");
    delay(2000);
    return;
  }

  // Buat data JSON
  JsonDocument doc;
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

  // Tunggu 30 detik sebelum mengirim data lagi
  delay(5000);
}