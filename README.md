# 🌡️ Multi-Node Temperature Monitoring System# Proyek Monitoring Suhu dan Kelembapan Real-time Berbasis IoT

Sistem monitoring suhu dan├── 📁 src/
│ ├── 📁 mu├── ⚡ run*dashboard.bat # Quick start single-node web dashboard
├── 📈 run_analysis.bat # Quick start historical data analysis
├── 🗺️ run_heatmap.bat # Quick start multi-node heatmap dashboard
└── 📈 run_linechart.bat # Quick start multi-node line chart dashboardnode/ # 🆕 Multi-Node System
│ │ ├── 🗺️ heatmap_dashboard.py # Dashboard heatmap (Port 8050)
│ │ ├── 📈 line_chart_dashboard.py # Dashboard line chart (Port 8051)
│ │ ├── 🔧 node_simulator.py # Simulator multi-node
│ │ └── 🖥️ esp32_multi_node.cpp # ESP32 code for multi-node deployment
│ └── 📁 single_node/ # 🔄 Single-Node System (Legacy)
│ ├── 📊 dashboard.py # Single-node web dashboard
│ ├── 📈 analisis.py # Historical data analysis
│ ├── 🔧 main.cpp # Single-node ESP32 code
│ └── ⚙️ diagram.json # Wokwi simulator config real-time berbasis IoT dengan dukungan **multi-node deployment** dan visualisasi **heatmap interaktif**. Proyek ini menggabungkan monitoring single-node tradisional dengan kemampuan multi-node untuk monitoring area yang lebih luas.Selamat datang di proyek monitoring IoT \_end-to-end*. Sistem ini dirancang untuk mengambil data suhu dan kelembapan dari sensor, mengirimkannya melalui protokol MQTT, menyimpannya dalam database, dan menampilkannya secara _real-time_ melalui dua opsi visualisasi: **dasbor web interaktif** (Plotly & Dash) atau **aplikasi desktop sederhana** (Matplotlib & Tkinter).

## 🚀 Sistem Multi-Node (Fitur Utama)Selain monitoring langsung, proyek ini juga dilengkapi dengan skrip untuk **analisis data historis** guna mengekstrak wawasan dari data yang telah terkumpul.

Sistem ini dirancang untuk monitoring **field/area besar** dengan multiple sensor nodes yang bekerja secara koordinatif untuk memberikan gambaran distribusi suhu dalam bentuk **heatmap real-time**.## Fitur Utama

### Fitur Multi-Node:- **Monitoring Real-time**: Lihat data suhu dan kelembapan saat itu juga.

- **Multi-Node Support**: Mendukung unlimited sensor nodes dengan identitas unik- **Pencatatan Data Historis**: Semua data sensor disimpan dalam database lokal SQLite untuk analisis di kemudian hari.

- **Heatmap Visualization**: Visualisasi distribusi suhu dalam bentuk gradient heatmap - **Dua Opsi Visualisasi**:

- **Line Chart Dashboard**: Monitoring tren suhu per node dalam diagram garis 1. **Dasbor Web (Direkomendasikan)**: Antarmuka modern, interaktif, dan dapat diakses melalui browser, dibangun dengan Plotly & Dash.

- **Field Coverage**: Setiap node memantau area dalam radius 15 meter 2. **Aplikasi Desktop**: Jendela aplikasi sederhana yang ringan dan berjalan secara native di OS Anda, dibangun dengan Matplotlib & Tkinter.

- **Node Status Tracking**: Deteksi otomatis status node (online/offline)- **Arsitektur Berbasis MQTT**: Menggunakan protokol MQTT yang ringan dan efisien, standar industri untuk komunikasi IoT.

- **Fault Tolerance**: Sistem tetap berjalan meski beberapa node mati- **Simulasi Hardware**: Proyek ini dapat dijalankan sepenuhnya menggunakan simulator Wokwi, tanpa memerlukan perangkat keras fisik.

- **Real-time Updates**: Data terupdate setiap 1-2 detik

## Topologi / Arsitektur Sistem

### Single-Node Legacy:

Proyek ini juga tetap mendukung monitoring single-node tradisional dengan opsi visualisasi web dashboard atau aplikasi desktop.Sistem ini terdiri dari beberapa komponen yang saling terhubung untuk membentuk alur data yang mulus dari sensor hingga ke antarmuka pengguna.

## 📋 Fitur Lengkap```mermaid

graph TD

- **Monitoring Real-time**: Lihat data suhu dan kelembapan saat itu juga subgraph "Sensor Node"

- **Multi-Dashboard**: Pilih antara heatmap, line chart, atau single-node dashboard A[ESP32 + DHT22] -->|Membaca Data| B(Format Data ke JSON);

- **Pencatatan Data Historis**: Semua data sensor disimpan dalam database SQLite end

- **Arsitektur MQTT**: Protokol lightweight dan efisien untuk komunikasi IoT

- **Simulasi Hardware**: Dapat dijalankan tanpa hardware menggunakan simulator subgraph "Komunikasi"

- **Node Management**: Auto-detect dan status tracking untuk semua node C(Broker MQTT HiveMQ);

  end

## 🗃️ Arsitektur Sistem

    subgraph "Backend Lokal"

````mermaid D[Skrip Python] -->|Menyimpan Data| E(Database SQLite 'climate_data.db');

graph TD    end

    subgraph "Multi-Node Sensors"

        A1[ESP32 + DHT22 Node_001]     subgraph "Visualisasi & Analisis"

        A2[ESP32 + DHT22 Node_002]        F[Opsi 1: Dashboard Web (Dash)] -->|Membaca 50 data terakhir| E;

        A3[ESP32 + DHT22 Node_003]        G[Opsi 2: Aplikasi Desktop (Matplotlib)] -->|Membaca 50 data terakhir| E;

        AN[ESP32 + DHT22 Node_N]        H[Opsi 3: Skrip Analisis Historis] -->|Membaca SEMUA data| E;

    end    end



    subgraph "Communication"    B -->|Publish ke Topik '0013/climate'| C;

        C(MQTT Broker HiveMQ)    C -->|Subscribe ke Topik '0013/climate'| D;

    end```



    subgraph "Data Processing"## Teknologi yang Digunakan

        D[Python MQTT Subscriber]

        E[(SQLite Database)]- **Hardware / Simulasi**:

    end  - Mikrokontroler: **ESP32 DevKitC V4**

  - Sensor: **DHT22** (suhu dan kelembapan)

    subgraph "Visualization Options"  - Simulator: **Wokwi**

        F1[🗺️ Heatmap Dashboard - Port 8050]- **Protokol Komunikasi**: **MQTT**

        F2[📈 Line Chart Dashboard - Port 8051] - **Broker MQTT**: **HiveMQ Public Broker** (`broker.hivemq.com`)

        F3[📊 Single Node Dashboard - Port 8052]- **Backend & Penyimpanan**:

        G[🖥️ Desktop App - Matplotlib]  - Bahasa: **Python 3**

    end  - Database: **SQLite**

- **Frontend / Visualisasi**:

    A1 -->|JSON Data| C  - **Opsi 1**: **Plotly & Dash** (untuk dasbor web)

    A2 -->|JSON Data| C  - **Opsi 2**: **Matplotlib & Tkinter** (untuk aplikasi desktop)

    A3 -->|JSON Data| C- **Lingkungan Pengembangan**:

    AN -->|JSON Data| C  - **Visual Studio Code** + Ekstensi **PlatformIO** & **Python**.



    C -->|Subscribe Multi-Node Topic| D## Struktur Folder

    D -->|Store Data| E

    ```

    E -->|Read Data| F1proyek-monitoring-suhu/

    E -->|Read Data| F2├── src/

    E -->|Read Data| F3│   ├── dashboard.py         # Opsi 1: Backend & Frontend untuk Plotly/Dash

    E -->|Read Data| G│   ├── gui.py               # Opsi 2: Backend & Frontend untuk Matplotlib/Tkinter

```│   ├── analisis.py          # Opsi 3: Skrip untuk analisis data historis

│   ├── main.cpp             # Kode firmware untuk ESP32

## 🗂️ Struktur Proyek│   └── diagram.json         # Konfigurasi sirkuit untuk Wokwi

├── 📁 src/
│   ├── 📁 multi_node/          # 🆕 Multi-Node System
│   │   ├── 🗺️ heatmap_dashboard.py      # Dashboard heatmap (Port 8050)
│   │   ├── 📈 line_chart_dashboard.py   # Dashboard line chart (Port 8051)
│   │   ├── 🔧 node_simulator.py         # Simulator multi-node
│   │   └── 🖥️ esp32_multi_node.cpp     # ESP32 code for multi-node deployment
│   ├── 📊 dashboard.py                  # Single-node web dashboard

│   ├── 📈 analisis.py                  # Historical data analysis
│   ├── � main.cpp                     # Single-node ESP32 code
│   └── ⚙️ diagram.json                # Wokwi simulator config
├── 📁 test/                            # Testing utilities
│   ├── 🧪 test_mqtt.py                 # MQTT connection testing
│   └── � README                       # Test documentation
├── 📋 requirements.txt                  # Python dependencies
├── 📖 README.md                        # This file
├── ⚡ run_dashboard.bat                # Quick start single-node web
├── 🖥️ run_gui.bat                     # Quick start desktop app
├── �️ run_heatmap.bat                 # Quick start heatmap dashboard
└── 📈 run_linechart.bat               # Quick start line chart dashboard
````

## 🚀 Quick Start Multi-Node

### Prasyarat

- [Python 3.8+](https://www.python.org/downloads/) terinstal. Pastikan untuk mencentang "Add Python to PATH" saat instalasi.
- [Visual Studio Code](https://code.visualstudio.com/) terinstal.
- Di dalam VS Code, instal ekstensi berikut:
  - `Python` (dari Microsoft)
  - `PlatformIO IDE` (untuk pengembangan ESP32)

├── 📋 requirements.txt # Python dependencies - `Wokwi Simulator`

├── 📖 README.md # This file

├── ⚡ run_dashboard.bat # Quick start single-node web### Langkah-langkah Instalasi

├── 🖥️ run_gui.bat # Quick start desktop app

├── 🗺️ run_heatmap.bat # Quick start heatmap dashboardProyek ini dilengkapi dengan skrip `.bat` untuk mengotomatiskan seluruh proses. Cukup jalankan salah satu skrip (`run_dashboard.bat` atau `run_gui.bat`), dan skrip tersebut akan menangani pembuatan virtual environment dan instalasi semua package dari `requirements.txt` secara otomatis.

└── 📈 run_linechart.bat # Quick start line chart dashboard

```## Menjalankan Sensor Node (ESP32)



## 🚀 Quick Start Multi-NodeIni adalah langkah pertama yang harus dilakukan agar ada data yang dikirim.



### 1. Setup Hardware (per Node)1.  Buka folder proyek ini di Visual Studio Code.

2.  Tekan `F1`, lalu ketik dan pilih **`Wokwi: Start Simulator`**.

**Komponen per node:**3.  Biarkan tab simulator ini tetap berjalan di latar belakang.

- ESP32 development board

- DHT22 atau DHT11 sensor_(Untuk alternatif menjalankan di browser, lihat bagian akhir dokumen ini.)_

- Kabel jumper dan breadboard

- Power supply (USB atau battery)---



**Wiring sederhana:**## Cara Menjalankan Aplikasi

```

DHT22 → ESP32Setelah sensor berjalan, Anda dapat memilih salah satu dari tiga opsi berikut.

VCC → 3.3V

GND → GND ### Opsi 1: Visualisasi Web dengan Plotly & Dash (Direkomendasikan)

DATA → GPIO 4

````Metode ini akan menjalankan server web lokal yang menampilkan dasbor interaktif dengan data 50 sensor terakhir dan analisis tren sesaat.



### 2. Konfigurasi Node ID- **Cara Otomatis (Windows)**:

  - Klik dua kali file **`run_dashboard.bat`**.

Edit untuk setiap ESP32:- **Cara Manual**:

  1.  Aktifkan virtual environment (`.venv\Scripts\activate`).

**Node 1:**  2.  Jalankan perintah: `python src/single_node/dashboard.py`

```cpp  3.  Buka browser Anda dan kunjungi alamat **`http://127.0.0.1:8050/`**.

const char* NODE_ID = "node_001";

const float POS_X = 25.0;   // Posisi X (meter)### Opsi 2: Visualisasi Desktop dengan Matplotlib & Tkinter

const float POS_Y = 25.0;   // Posisi Y (meter)

```Metode ini akan membuka jendela aplikasi desktop sederhana yang menampilkan 50 data sensor terakhir.



**Node 2:**- **Cara Otomatis (Windows)**:

```cpp  - Klik dua kali file **`run_gui.bat`**.

const char* NODE_ID = "node_002"; - **Cara Manual**:

const float POS_X = 75.0;  1.  Aktifkan virtual environment (`.\venv\Scripts\activate`).

const float POS_Y = 25.0;  2.  Jalankan perintah: `python src/single_node/gui.py` (file tidak tersedia dalam versi ini)

````

### Opsi 3: Analisis Data Historis

**Node 3:**

````cppGunakan skrip ini setelah Anda mengumpulkan data selama beberapa waktu (misalnya, beberapa jam atau hari). Skrip ini akan membaca **seluruh data** dari database dan menampilkan jendela grafik interaktif untuk analisis mendalam.

const char* NODE_ID = "node_003";

const float POS_X = 50.0;- **Cara Menjalankan**:

const float POS_Y = 75.0;  1.  Pastikan aplikasi real-time (Opsi 1 atau 2) tidak sedang berjalan.

```  2.  Buka terminal baru dan aktifkan virtual environment (`.\venv\Scripts\activate`).

  3.  Jalankan perintah:

### 3. Upload Code ke ESP32      ```bash

      python src/single_node/analisis.py

1. Buka `src/multi_node/esp32_multi_node.cpp` di Arduino IDE      ```

2. Edit WiFi SSID dan password  - Sebuah jendela akan muncul menampilkan dua plot: data mentah dan analisis tren suhu jangka panjang. Anda dapat menggunakan toolbar di jendela tersebut untuk men-zoom dan menggeser grafik.

3. Edit Node ID dan posisi sesuai kebutuhan

4. Upload ke masing-masing ESP32---



### 4. Jalankan Dashboard## Informasi Tambahan



**Heatmap Dashboard (Recommended):**### Cara Mengakses Database SQLite

```bash

cd src/multi_nodeSemua data historis disimpan dalam file `climate_data.db`. Anda bisa membukanya menggunakan aplikasi gratis seperti **DB Browser for SQLite** ([sqlitebrowser.org](https://sqlitebrowser.org/dl/)) untuk melihat, memfilter, atau mengekspor data dalam format spreadsheet.

python heatmap_dashboard.py

```### Alternatif Menjalankan Wokwi (di Browser)

Akses: `http://127.0.0.1:8050`

Jika Anda tidak menggunakan VS Code, Anda bisa menjalankan simulasi langsung di situs Wokwi.

**Line Chart Dashboard:**

```bash1.  Buka [wokwi.com](https://wokwi.com/).

cd src/multi_node  2.  Buat proyek baru dengan memilih template **ESP32**.

python line_chart_dashboard.py3.  Salin seluruh isi file **`main.cpp`** dari proyek ini dan tempelkan ke tab `sketch.cpp` di Wokwi.

```4.  Salin seluruh isi file **`diagram.json`** dari proyek ini dan tempelkan ke tab `diagram.json` di Wokwi.

Akses: `http://127.0.0.1:8051`5.  Klik tombol **Start Simulation** (panah hijau).


### 5. Testing dengan Simulator

Untuk testing tanpa hardware:
```bash
cd src/multi_node
python node_simulator.py
````

## 📊 Dashboard Options

### 🗺️ Heatmap Dashboard (Port 8050)

- **Field view**: Area 100x100m dengan grid koordinat
- **Temperature gradient**: Visualisasi distribusi suhu dengan color scale
- **Node positions**: Marker menunjukkan posisi dan status setiap node
- **Coverage area**: Lingkaran menunjukkan radius coverage (15m)
- **Real-time updates**: Auto-refresh setiap 2 detik
- **Node status**: Panel status menampilkan info setiap node

### 📈 Line Chart Dashboard (Port 8051)

- **Temperature trends**: Grafik garis tren suhu per node
- **Humidity trends**: Grafik garis tren kelembapan per node
- **Combined overview**: Grafik gabungan semua node
- **Time series**: Data dengan timestamp untuk analisis tren
- **Interactive legends**: Klik untuk show/hide node tertentu
- **Node status cards**: Status dan data terakhir setiap node

### 📊 Single-Node Dashboard (Legacy)

Dashboard tradisional untuk monitoring single sensor dengan gauge dan chart.

## 🗄️ Database Schema

### Multi-Node Database (`multi_node_climate.db`)

**Table: `climate_data`**

```sql
CREATE TABLE climate_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id TEXT NOT NULL,
    temperature REAL NOT NULL,
    humidity REAL NOT NULL,
    pos_x REAL,
    pos_y REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Table: `node_info`**

```sql
CREATE TABLE node_info (
    node_id TEXT PRIMARY KEY,
    pos_x REAL NOT NULL,
    pos_y REAL NOT NULL,
    last_seen DATETIME,
    status TEXT DEFAULT 'active'
);
```

## 📡 MQTT Protocol

### Topic Structure

```
Informatika/IoT-E/Kelompok9/multi_node/{node_id}
```

**Contoh:**

- `Informatika/IoT-E/Kelompok9/multi_node/node_001`
- `Informatika/IoT-E/Kelompok9/multi_node/node_002`
- `Informatika/IoT-E/Kelompok9/multi_node/node_003`

### JSON Data Format

```json
{
  "node_id": "node_001",
  "temperature": 25.6,
  "humidity": 60.2,
  "pos_x": 25.0,
  "pos_y": 25.0,
  "timestamp": 1695123456.789
}
```

## 🔧 Hardware Guide

### Komponen yang Dibutuhkan (per Node)

| Komponen      | Spesifikasi              | Keterangan                      |
| ------------- | ------------------------ | ------------------------------- |
| **ESP32**     | ESP32-WROOM-32           | Mikrokontroler utama            |
| **DHT22**     | -40°C to 80°C, 0-100% RH | Sensor suhu & kelembapan akurat |
| **DHT11**     | 0-50°C, 20-90% RH        | Alternatif lebih murah          |
| **Resistor**  | 10kΩ                     | Pull-up untuk DHT               |
| **Power**     | 5V/1A USB atau Battery   | Catu daya                       |
| **Enclosure** | IP65 (outdoor)           | Proteksi cuaca                  |

### Pin Assignment

```cpp
#define DHT_PIN 4           // Data pin DHT22
#define LED_WIFI_PIN 2      // Built-in LED untuk status WiFi
#define LED_MQTT_PIN 12     // External LED untuk status MQTT
```

### Field Layout Contoh

```
Field Area: 100m x 100m

     85m  •NODE_004    •NODE_005  85m
          (15,85)      (85,85)

     75m        •NODE_003
                (50,75)

     25m  •NODE_001    •NODE_002  25m
          (25,25)      (75,25)

          25m    50m    75m
```

## 🛠️ Installation & Setup

### Prerequisites

- **Python 3.8+** dengan pip
- **Arduino IDE** untuk ESP32 programming
- **VS Code** dengan ekstensi PlatformIO (optional)

### Python Dependencies

```bash
pip install -r requirements.txt
```

**Main libraries:**

- `dash>=3.2.0` - Web dashboard framework
- `plotly>=6.3.0` - Interactive charts
- `paho-mqtt>=2.1.0` - MQTT client
- `pandas>=2.3.2` - Data processing
- `numpy>=2.3.3` - Numerical computing

### ESP32 Libraries (Arduino IDE)

```
Tools → Manage Libraries → Install:
- ArduinoJson by Benoit Blanchon
- DHT sensor library by Adafruit
- Adafruit Unified Sensor
- PubSubClient by Nick O'Leary
```

## 🔍 Monitoring & Debugging

### Serial Monitor Output

```
=== ESP32 Multi-Node Sensor ===
Node ID: node_001
Position: (25.0, 25.0)
WiFi terhubung! IP: 192.168.1.100
MQTT terhubung!
[node_001] T:25.1°C H:65.0% ✓
[node_001] T:25.2°C H:64.8% ✓
```

### LED Status Indicators

- **WiFi LED (GPIO 2)**: 🟢 = Connected, 🔴 = Disconnected
- **MQTT LED (GPIO 12)**: 🟢 = Connected, 🔴 = Disconnected
- **Blinking**: Connection in progress

### Dashboard Status

- **Online Node**: 🟢 Hijau dengan data real-time
- **Offline Node**: 🔴 Merah jika tidak ada data >30 detik
- **Data Retention**: Node offline tetap ditampilkan dengan data terakhir

## 🎯 Use Cases

### Smart Agriculture

- Monitoring suhu dan kelembapan tanah di berbagai area lahan
- Deteksi hotspots atau area kering
- Optimasi sistem irigasi berdasarkan data heatmap

### Industrial Monitoring

- Monitoring suhu proses di berbagai zona pabrik
- Warehouse temperature monitoring untuk cold storage
- Quality control dalam proses manufaktur

### Environmental Research

- Monitoring iklim mikro di area penelitian
- Urban heat island studies
- Climate change impact assessment

### Smart Buildings

- HVAC monitoring dan kontrol per zona
- Energy efficiency optimization
- Comfort level monitoring per area

## 🔧 Customization

### Menambah Node Baru

1. **Hardware**: Setup ESP32 + DHT22 dengan wiring standard
2. **Software**: Edit `esp32_multi_node.cpp` dengan unique node_id dan posisi
3. **Dashboard**: Otomatis detect node baru tanpa perubahan code

### Mengubah Field Size

Edit di dashboard files:

```python
FIELD_WIDTH = 200    # Sesuaikan dengan area monitoring
FIELD_HEIGHT = 150
NODE_RADIUS = 25     # Radius coverage per node
```

### Custom Color Scale

```python
colorscale='RdYlBu_r'   # Red-Yellow-Blue
# Options: 'Viridis', 'Plasma', 'Hot', 'Cool', dll
```

## 📈 Data Analysis

### Historical Data Access

Database SQLite dapat diakses dengan:

- **DB Browser for SQLite** untuk GUI
- **Python pandas** untuk programmatic analysis
- **SQL queries** untuk custom reporting

### Export Data

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('multi_node_climate.db')
df = pd.read_sql_query("SELECT * FROM climate_data", conn)
df.to_csv('temperature_data.csv', index=False)
```

## 🛡️ Security & Production

### Production Deployment

```cpp
// Use secured MQTT broker
const char* mqtt_username = "your_username";
const char* mqtt_password = "your_password";

// Enable WPA2 Enterprise for WiFi
// Add SSL/TLS for MQTT communication
```

### Data Backup

```bash
# Automated backup script
cp multi_node_climate.db backup/climate_data_$(date +%Y%m%d).db
```

## 📞 Support & Troubleshooting

### Common Issues

**WiFi Connection Failed:**

- Pastikan SSID dan password benar
- Gunakan WiFi 2.4GHz (bukan 5GHz)
- Check signal strength di lokasi node

**MQTT Connection Failed:**

- Verify internet connection
- Check firewall settings
- Try different MQTT broker jika diperlukan

**No Data in Dashboard:**

- Check Serial Monitor untuk error messages
- Verify JSON format di MQTT message
- Pastikan topic subscription sesuai

**Sensor Reading NaN:**

- Check DHT wiring connections
- Try different GPIO pin
- Replace sensor jika rusak

### Getting Help

1. Check Serial Monitor output untuk detailed error messages
2. Verify MQTT connection dengan `test/test_mqtt.py`
3. Check database content dengan SQLite browser
4. Monitor network traffic dengan MQTT client tools

## 🎉 Quick Demo

**Untuk demo cepat tanpa hardware:**

1. **Start Simulator:**

   ```bash
   cd src/multi_node
   python node_simulator.py
   ```

2. **Start Dashboard:**

   ```bash
   python heatmap_dashboard.py
   ```

3. **Open Browser:**
   `http://127.0.0.1:8050`

4. **See Results:**
   - 3 virtual nodes akan muncul di heatmap
   - Data berubah setiap 1-2 detik
   - Temperature gradient otomatis terupdate

**Selamat! Multi-node temperature monitoring system siap digunakan! 🎉**

---

## 📄 Legacy Single-Node Documentation

### Fitur Single-Node

- **Monitoring Real-time**: Data suhu dan kelembapan dari satu sensor
- **Dual Visualization**: Web dashboard (Dash) atau desktop app (Tkinter)
- **Historical Analysis**: Analisis data historis dengan trend analysis

### Cara Menjalankan Single-Node

**Web Dashboard:**

```bash
python src/single_node/dashboard.py
```

Akses: `http://127.0.0.1:8052`

**Desktop App:**

```bash
python src/single_node/gui.py
```

**Historical Analysis:**

```bash
python src/single_node/analisis.py
```

### Single-Node Hardware

- ESP32 + DHT22 dengan kode di `src/single_node/main.cpp`
- Wokwi simulator dengan `src/single_node/diagram.json`
- Database: `climate_data.db`
- MQTT Topic: `0013/climate`

Sistem single-node tetap kompatibel dan dapat digunakan bersamaan dengan sistem multi-node.
