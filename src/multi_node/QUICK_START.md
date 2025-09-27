# Quick Start Guide - ESP32 Multi-Node Deployment

## 🚀 Langkah Cepat Setup Node

### 1. Persiapan Hardware

**Yang dibutuhkan per node:**

- ESP32 board
- DHT22 atau DHT11 sensor
- Kabel jumper 3 buah
- Breadboard (opsional)

**Wiring Simple:**

```
DHT22    →    ESP32
VCC      →    3.3V
GND      →    GND
DATA     →    GPIO 4
```

### 2. Setup Arduino IDE

```bash
# Install libraries:
- ArduinoJson
- DHT sensor library
- PubSubClient
- Adafruit Unified Sensor
```

### 3. Konfigurasi Code per Node

**Node 1:**

```cpp
const char* NODE_ID = "node_001";
const float POS_X = 25.0;
const float POS_Y = 25.0;
```

**Node 2:**

```cpp
const char* NODE_ID = "node_002";
const float POS_X = 75.0;
const float POS_Y = 25.0;
```

**Node 3:**

```cpp
const char* NODE_ID = "node_003";
const float POS_X = 50.0;
const float POS_Y = 75.0;
```

### 4. Upload & Test

1. Edit `esp32_simple.cpp` dengan konfigurasi node
2. Ganti WiFi SSID dan password
3. Upload ke ESP32
4. Buka Serial Monitor (115200 baud)
5. Lihat output: `[node_001] T:25.1°C H:65.0% ✓`

### 5. Jalankan Dashboard

```bash
cd src/multi_node
python heatmap_dashboard.py
```

Buka: `http://127.0.0.1:8050`

## 🗺️ Contoh Layout Field

```
Field 100m x 100m:

     NODE_003
     (50,75)
        •

NODE_001      NODE_002
(25,25)       (75,25)
   •             •
```

## 📊 Expected Output

**Serial Monitor:**

```
=== ESP32 Multi-Node Sensor ===
Node ID: node_001
Position: (25.0, 25.0)
WiFi terhubung!
IP: 192.168.1.100
Menghubungkan ke MQTT... terhubung!
Setup selesai!
[node_001] T:25.1°C H:65.0% ✓
[node_001] T:25.2°C H:64.8% ✓
```

**Dashboard:**

- ● node_001 T: 25.1°C H: 65.0% Pos: (25.0, 25.0) Status: online
- ● node_002 T: 26.5°C H: 62.3% Pos: (75.0, 25.0) Status: online
- ● node_003 T: 27.8°C H: 58.9% Pos: (50.0, 75.0) Status: online

## ⚡ Quick Troubleshooting

**WiFi tidak connect:**

- Cek SSID dan password
- Pastikan WiFi 2.4GHz (bukan 5GHz)

**MQTT tidak connect:**

- Cek koneksi internet
- Restart ESP32

**Sensor tidak terbaca:**

- Cek wiring DHT22
- Ganti dengan DHT11 jika perlu

**Data tidak muncul di dashboard:**

- Pastikan topic MQTT sesuai
- Cek format JSON di Serial Monitor

## 📁 File Structure

```
src/multi_node/
├── esp32_simple.cpp         # ← Upload ini ke ESP32
├── heatmap_dashboard.py     # ← Jalankan untuk dashboard
├── node_simulator.py        # ← Untuk testing tanpa hardware
├── README.md               # ← Dokumentasi lengkap
└── HARDWARE_GUIDE.md       # ← Panduan hardware detail
```

## 🎯 Next Steps

1. **Testing**: Gunakan `node_simulator.py` untuk testing dashboard tanpa hardware
2. **Scaling**: Tambah lebih banyak node dengan ID dan posisi berbeda
3. **Monitoring**: Dashboard akan otomatis update setiap 2 detik
4. **Analysis**: Data tersimpan di database `multi_node_climate.db`

**Selamat! Multi-node monitoring system sudah siap digunakan! 🎉**
