# Multi-Node Temperature Field Monitoring System

Sistem monitoring suhu multi-node dengan visualisasi heatmap real-time untuk pemantauan area/field dengan multiple sensor nodes.

## 📋 Fitur Utama

- **Multi-Node Support**: Mendukung multiple sensor nodes dengan identitas unik
- **Heatmap Visualization**: Visualisasi panas dalam bentuk heatmap dengan gradient suhu
- **Real-time Monitoring**: Update data real-time dari semua node aktif
- **Node Status Tracking**: Deteksi otomatis status node (online/offline)
- **Field Coverage**: Setiap node memantau area dalam radius tertentu
- **Data Persistence**: Penyimpanan data ke database SQLite terpisah
- **Fault Tolerance**: Tetap menampilkan data terakhir jika node mati

## 🗃️ Struktur Database

### Tabel `multi_node_climate`

```sql
CREATE TABLE multi_node_climate (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    temperature REAL NOT NULL,
    humidity REAL NOT NULL,
    pos_x REAL NOT NULL,
    pos_y REAL NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

### Tabel `node_info`

```sql
CREATE TABLE node_info (
    node_id TEXT PRIMARY KEY,
    pos_x REAL NOT NULL,
    pos_y REAL NOT NULL,
    radius REAL DEFAULT 15.0,
    status TEXT DEFAULT 'active',
    last_seen DATETIME,
    description TEXT
)
```

## 📡 Format Data MQTT

Setiap node mengirim data dengan format JSON berikut:

```json
{
  "node_id": "node_001",
  "temperature": 25.6,
  "humidity": 60.2,
  "pos_x": 20.0,
  "pos_y": 30.0,
  "timestamp": 1695123456.789
}
```

**MQTT Topic Pattern**: `Informatika/IoT-E/Kelompok9/multi_node/{node_id}`

## ⚙️ Konfigurasi Sistem

### Parameter Field

- **FIELD_WIDTH**: 100 meter (lebar area monitoring)
- **FIELD_HEIGHT**: 100 meter (tinggi area monitoring)
- **NODE_RADIUS**: 15 meter (radius coverage per node)
- **GRID_RESOLUTION**: 5 meter (resolusi grid heatmap)

### Parameter Node

- **NODE_TIMEOUT**: 30 detik (timeout untuk menganggap node offline)
- **Update Interval**: 1-10 detik (dapat diatur melalui dashboard)

## 🚀 Cara Menjalankan

### 1. Persiapan Environment

```bash
# Install dependencies (jika belum ada)
pip install dash plotly paho-mqtt numpy sqlite3
```

### 2. Jalankan Dashboard

```bash
cd src/multi_node
python heatmap_dashboard.py
```

Dashboard akan tersedia di: `http://127.0.0.1:8050`

### 3. Jalankan Simulator (untuk Testing)

```bash
# Di terminal terpisah
python node_simulator.py
```

### 4. Menggunakan Node Fisik

Untuk ESP32 atau mikrocontroller lain, kirim data ke MQTT broker dengan format JSON di atas ke topik yang sesuai.

## 📊 Interface Dashboard

### Status Nodes Panel

- Menampilkan status setiap node (online/offline)
- Data terakhir dari setiap node (suhu, kelembaban, posisi)
- Indikator visual dengan color coding

### Heatmap Visualization

- Field area dengan grid koordinat
- Gradient warna berdasarkan suhu (merah = panas, biru = dingin)
- Posisi node ditandai dengan marker
- Lingkaran menunjukkan radius coverage node
- Hover tooltip untuk detail data

### Controls

- Slider untuk mengatur interval update (1-10 detik)
- Auto-refresh untuk data real-time

## 🔧 Simulasi Testing

File `node_simulator.py` menyediakan simulator untuk testing dengan 3 node virtual:

- **node_001**: Posisi (25, 25) - Base temp 28°C
- **node_002**: Posisi (75, 25) - Base temp 26.5°C
- **node_003**: Posisi (50, 75) - Base temp 30°C

Setiap node menghasilkan data dengan variasi realistis dan noise.

## 📈 Algoritma Heatmap

1. **Grid Generation**: Membuat grid koordinat berdasarkan FIELD_SIZE dan GRID_RESOLUTION
2. **Distance Calculation**: Untuk setiap titik grid, hitung jarak ke semua node aktif
3. **Weight Assignment**: Node dalam radius mendapat weight berdasarkan inverse distance
4. **Temperature Interpolation**: Weighted average temperature dari node dalam radius
5. **Visualization**: Render heatmap dengan color scale

## 🔍 Monitoring Node Status

- **Online**: Node mengirim data dalam NODE_TIMEOUT terakhir
- **Offline**: Node tidak mengirim data > NODE_TIMEOUT
- **Data Retention**: Data terakhir node offline tetap ditampilkan di heatmap

## 🛠️ Kustomisasi

### Menambah Node Baru

1. Tambahkan konfigurasi node di `node_simulator.py` (untuk testing)
2. Atau konfigurasikan ESP32/hardware untuk mengirim data ke MQTT

### Mengubah Field Size

Edit parameter di `heatmap_dashboard.py`:

```python
FIELD_WIDTH = 200  # Ganti sesuai kebutuhan
FIELD_HEIGHT = 150
NODE_RADIUS = 25
```

### Custom Color Scale

Ganti parameter colorscale di heatmap:

```python
colorscale='RdYlBu_r'  # Red-Yellow-Blue
# Atau: 'Viridis', 'Plasma', 'Hot', dll
```

## 🗄️ File Database

- **multi_node_climate.db**: Database baru khusus multi-node
- **climate_data.db**: Database lama (single node) tetap tersedia

## 🔗 Integrasi dengan Hardware

Untuk ESP32/Arduino, contoh kode pengiriman data:

```cpp
// JSON payload
String payload = "{";
payload += "\"node_id\":\"" + String(NODE_ID) + "\",";
payload += "\"temperature\":" + String(temperature) + ",";
payload += "\"humidity\":" + String(humidity) + ",";
payload += "\"pos_x\":" + String(POS_X) + ",";
payload += "\"pos_y\":" + String(POS_Y) + ",";
payload += "\"timestamp\":" + String(millis()/1000.0);
payload += "}";

// Publish ke MQTT
String topic = "Informatika/IoT-E/Kelompok9/multi_node/" + String(NODE_ID);
mqttClient.publish(topic.c_str(), payload.c_str());
```

## 🎯 Use Cases

- **Smart Agriculture**: Monitoring suhu tanah/udara di lahan pertanian
- **Warehouse Monitoring**: Pengawasan suhu ruangan penyimpanan
- **Environmental Research**: Monitoring iklim mikro area penelitian
- **Industrial Process**: Monitoring suhu proses produksi multi-zona
- **Smart Building**: HVAC monitoring dan kontrol per area

## 📞 Support

Untuk pertanyaan atau issue:

1. Cek log error di console
2. Pastikan MQTT broker dapat diakses
3. Verifikasi format JSON data yang dikirim
4. Periksa koneksi database SQLite
