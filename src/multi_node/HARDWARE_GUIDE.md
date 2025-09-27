# ESP32 Multi-Node Temperature Monitoring - Hardware Guide

## 📋 Komponen yang Dibutuhkan per Node

### Hardware Utama

- **ESP32 Development Board** (ESP32-WROOM-32 atau sejenisnya)
- **DHT22 atau DHT11** sensor suhu & kelembaban
- **Resistor 10kΩ** (pull-up untuk DHT)
- **LED** (opsional, untuk indikator status)
- **Resistor 220Ω** (untuk LED)
- **Breadboard** atau **PCB Proto**
- **Kabel jumper**
- **Power supply 5V** atau **USB cable**

### Sensor Options

| Sensor | Range Suhu | Range Kelembaban | Akurasi | Harga  |
| ------ | ---------- | ---------------- | ------- | ------ |
| DHT11  | 0-50°C     | 20-90%           | ±2°C    | Murah  |
| DHT22  | -40-80°C   | 0-100%           | ±0.5°C  | Sedang |

## 🔌 Diagram Wiring

### Wiring DHT22/DHT11 ke ESP32

```
DHT22/DHT11          ESP32
┌─────────────┐    ┌─────────────┐
│   VCC   ────┼────┤ 3.3V        │
│   GND   ────┼────┤ GND         │
│   DATA  ────┼────┤ GPIO 4      │
│   NC        │    │             │
└─────────────┘    └─────────────┘
        │
    10kΩ ↑ (Pull-up resistor)
        │
       3.3V
```

### Wiring dengan LED Status (Opsional)

```
ESP32                LED Status
┌─────────────┐
│ GPIO 2  ────┼─── LED WiFi (Built-in)
│ GPIO 12 ────┼─── 220Ω ─── LED MQTT ─── GND
│             │
└─────────────┘
```

## 📌 Pin Assignment per Node

### Node 001

```cpp
#define DHT_PIN 4
#define LED_MQTT_PIN 12
const char* NODE_ID = "node_001";
const float POS_X = 25.0;
const float POS_Y = 25.0;
```

### Node 002

```cpp
#define DHT_PIN 4
#define LED_MQTT_PIN 12
const char* NODE_ID = "node_002";
const float POS_X = 75.0;
const float POS_Y = 25.0;
```

### Node 003

```cpp
#define DHT_PIN 4
#define LED_MQTT_PIN 12
const char* NODE_ID = "node_003";
const float POS_X = 50.0;
const float POS_Y = 75.0;
```

## 🛠️ Setup ESP32 IDE

### 1. Install Arduino IDE

- Download dari [arduino.cc](https://www.arduino.cc/en/software)
- Install ESP32 board package

### 2. Install ESP32 Board Package

```
File → Preferences → Additional Boards Manager URLs:
https://dl.espressif.com/dl/package_esp32_index.json

Tools → Board → Boards Manager → Search "ESP32" → Install
```

### 3. Install Required Libraries

```
Tools → Manage Libraries → Install:
- ArduinoJson by Benoit Blanchon
- DHT sensor library by Adafruit
- Adafruit Unified Sensor
- PubSubClient by Nick O'Leary
```

## ⚙️ Configuration Steps

### 1. WiFi Configuration

Edit di `esp32_node.cpp`:

```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
```

### 2. Node Configuration

Edit untuk setiap node:

```cpp
const char* NODE_ID = "node_XXX";    // Unique ID
const float POS_X = 25.0;            // X coordinate (meters)
const float POS_Y = 25.0;            // Y coordinate (meters)
```

### 3. Upload Code

```
Tools → Board → ESP32 Dev Module
Tools → Port → (Select your COM port)
Sketch → Upload
```

## 📡 MQTT Topics Structure

### Data Topic (per node)

```
Informatika/IoT-E/Kelompok9/multi_node/node_001
Informatika/IoT-E/Kelompok9/multi_node/node_002
Informatika/IoT-E/Kelompok9/multi_node/node_003
```

### Control Topic (optional)

```
Informatika/IoT-E/Kelompok9/multi_node/node_001/control
```

### Status Topic (optional)

```
Informatika/IoT-E/Kelompok9/multi_node/node_001/status
```

## 🔍 Testing & Debugging

### Serial Monitor Commands

Buka Serial Monitor (115200 baud) dan ketik:

- `info` - Show system information
- `test` - Send test data to MQTT
- `restart` - Restart ESP32
- `status` - Send status message

### LED Status Indicators

- **WiFi LED (GPIO 2)**: ON = WiFi Connected
- **MQTT LED (GPIO 12)**: ON = MQTT Connected
- **Blinking**: Connection in progress
- **OFF**: Disconnected

### Troubleshooting

#### WiFi Connection Issues

```cpp
// Check signal strength
Serial.println(WiFi.RSSI());

// Check IP address
Serial.println(WiFi.localIP());
```

#### MQTT Connection Issues

```cpp
// Check MQTT state
Serial.println(client.state());
// -4 = connection timeout
// -3 = connection lost
// -2 = connect failed
// -1 = disconnected
//  0 = connected
```

#### Sensor Reading Issues

```cpp
// Check if sensor is wired correctly
float t = dht.readTemperature();
if (isnan(t)) {
  Serial.println("DHT read failed!");
}
```

## 🏗️ Physical Installation

### Field Deployment Layout

```
Field Area: 100m x 100m

     85m  •NODE_004      •NODE_005  85m
          (15,85)        (85,85)


     75m        •NODE_003
                (50,75)


     25m  •NODE_001      •NODE_002  25m
          (25,25)        (75,25)

          25m      50m      75m
```

### Mounting Considerations

1. **Weather Protection**: Use IP65 enclosure untuk outdoor
2. **Power Supply**: Solar panel + battery untuk remote location
3. **Antenna**: External WiFi antenna untuk jangkauan lebih jauh
4. **Sensor Placement**:
   - DHT22 dalam housing berlubang untuk airflow
   - Hindari direct sunlight
   - Ketinggian 1.5-2m dari tanah

### Power Options

#### USB Power (Indoor/Lab)

- Gunakan USB cable ke power adapter 5V/1A
- Stable dan mudah untuk testing

#### Battery Power (Outdoor)

```cpp
// Add deep sleep untuk hemat baterai
esp_sleep_enable_timer_wakeup(30 * 1000000); // 30 seconds
esp_deep_sleep_start();
```

#### Solar Power (Remote)

- Solar panel 5W + Li-ion battery 3000mAh
- Charge controller untuk protect battery
- Bisa tahan 2-3 hari tanpa sinar matahari

## 📊 Data Validation

### Expected JSON Format

```json
{
  "node_id": "node_001",
  "temperature": 25.6,
  "humidity": 60.2,
  "pos_x": 25.0,
  "pos_y": 25.0,
  "timestamp": 1695123456
}
```

### Sensor Range Validation

- **Temperature**: -40°C to 80°C (DHT22)
- **Humidity**: 0% to 100%
- **Position**: 0-100m (sesuai field size)

## 🔧 Advanced Configuration

### Custom Intervals per Node

```cpp
// Stagger intervals untuk avoid collision
const unsigned long MQTT_INTERVALS[] = {5000, 5500, 6000, 6500, 7000};
const unsigned long MQTT_INTERVAL = MQTT_INTERVALS[NODE_INDEX];
```

### OTA (Over-The-Air) Updates

```cpp
#include <ArduinoOTA.h>

void setup() {
  ArduinoOTA.begin();
}

void loop() {
  ArduinoOTA.handle();
  // ... existing code
}
```

### Watchdog Timer

```cpp
#include "esp_system.h"

void setup() {
  esp_task_wdt_init(30, true); // 30 second timeout
  esp_task_wdt_add(NULL);
}

void loop() {
  esp_task_wdt_reset(); // Reset watchdog
  // ... existing code
}
```

## 💡 Tips & Best Practices

1. **Unique Node IDs**: Gunakan MAC address sebagai bagian ID
2. **Error Handling**: Implement retry logic untuk connection failures
3. **Data Filtering**: Filter sensor noise dengan moving average
4. **Timezone**: Set proper timezone untuk timestamp accuracy
5. **Security**: Gunakan MQTT username/password untuk production
6. **Monitoring**: Log system health (uptime, memory, signal strength)

## 📞 Support & Resources

- **ESP32 Datasheet**: [Espressif Documentation](https://docs.espressif.com/)
- **DHT Library**: [Adafruit DHT Guide](https://learn.adafruit.com/dht)
- **MQTT Client**: [PubSubClient Examples](https://pubsubclient.knolleary.net/)
- **Troubleshooting**: Check Serial Monitor output untuk error messages
