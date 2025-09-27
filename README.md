# Proyek Monitoring Suhu dan Kelembapan Real-time Berbasis IoT

Selamat datang di proyek monitoring IoT _end-to-end_. Sistem ini dirancang untuk mengambil data suhu dan kelembapan dari sensor, mengirimkannya melalui protokol MQTT, menyimpannya dalam database, dan menampilkannya secara _real-time_ melalui dua opsi visualisasi: **dasbor web interaktif** (Plotly & Dash) atau **aplikasi desktop sederhana** (Matplotlib & Tkinter).

Selain monitoring langsung, proyek ini juga dilengkapi dengan skrip untuk **analisis data historis** guna mengekstrak wawasan dari data yang telah terkumpul.

## Fitur Utama

- **Monitoring Real-time**: Lihat data suhu dan kelembapan saat itu juga.
- **Pencatatan Data Historis**: Semua data sensor disimpan dalam database lokal SQLite untuk analisis di kemudian hari.
- **Dua Opsi Visualisasi**:
  1.  **Dasbor Web (Direkomendasikan)**: Antarmuka modern, interaktif, dan dapat diakses melalui browser, dibangun dengan Plotly & Dash.
  2.  **Aplikasi Desktop**: Jendela aplikasi sederhana yang ringan dan berjalan secara native di OS Anda, dibangun dengan Matplotlib & Tkinter.
- **Arsitektur Berbasis MQTT**: Menggunakan protokol MQTT yang ringan dan efisien, standar industri untuk komunikasi IoT.
- **Simulasi Hardware**: Proyek ini dapat dijalankan sepenuhnya menggunakan simulator Wokwi, tanpa memerlukan perangkat keras fisik.

## Topologi / Arsitektur Sistem

Sistem ini terdiri dari beberapa komponen yang saling terhubung untuk membentuk alur data yang mulus dari sensor hingga ke antarmuka pengguna.

```mermaid
graph TD
    subgraph "Sensor Node"
        A[ESP32 + DHT22] -->|Membaca Data| B(Format Data ke JSON);
    end

    subgraph "Komunikasi"
        C(Broker MQTT HiveMQ);
    end

    subgraph "Backend Lokal"
        D[Skrip Python] -->|Menyimpan Data| E(Database SQLite 'climate_data.db');
    end

    subgraph "Visualisasi & Analisis"
        F[Opsi 1: Dashboard Web (Dash)] -->|Membaca 50 data terakhir| E;
        G[Opsi 2: Aplikasi Desktop (Matplotlib)] -->|Membaca 50 data terakhir| E;
        H[Opsi 3: Skrip Analisis Historis] -->|Membaca SEMUA data| E;
    end

    B -->|Publish ke Topik '0013/climate'| C;
    C -->|Subscribe ke Topik '0013/climate'| D;
```

## Teknologi yang Digunakan

- **Hardware / Simulasi**:
  - Mikrokontroler: **ESP32 DevKitC V4**
  - Sensor: **DHT22** (suhu dan kelembapan)
  - Simulator: **Wokwi**
- **Protokol Komunikasi**: **MQTT**
- **Broker MQTT**: **HiveMQ Public Broker** (`broker.hivemq.com`)
- **Backend & Penyimpanan**:
  - Bahasa: **Python 3**
  - Database: **SQLite**
- **Frontend / Visualisasi**:
  - **Opsi 1**: **Plotly & Dash** (untuk dasbor web)
  - **Opsi 2**: **Matplotlib & Tkinter** (untuk aplikasi desktop)
- **Lingkungan Pengembangan**:
  - **Visual Studio Code** + Ekstensi **PlatformIO** & **Python**.

## Struktur Folder

```
proyek-monitoring-suhu/
├── src/
│   ├── dashboard.py         # Opsi 1: Backend & Frontend untuk Plotly/Dash
│   ├── gui.py               # Opsi 2: Backend & Frontend untuk Matplotlib/Tkinter
│   ├── analisis.py          # Opsi 3: Skrip untuk analisis data historis
│   ├── main.cpp             # Kode firmware untuk ESP32
│   └── diagram.json         # Konfigurasi sirkuit untuk Wokwi
├── .venv/                   # Folder virtual environment (dibuat otomatis)
├── requirements.txt         # Daftar semua package Python yang dibutuhkan
├── run_dashboard.bat        # Skrip untuk menjalankan dasbor web
└── run_gui.bat              # Skrip untuk menjalankan aplikasi desktop
```

## Panduan Setup (Wajib Dilakukan Pertama Kali)

Sebelum menjalankan aplikasi, Anda perlu menyiapkan lingkungan pengembangan.

### Prasyarat

- [Python 3.8+](https://www.python.org/downloads/) terinstal. Pastikan untuk mencentang "Add Python to PATH" saat instalasi.
- [Visual Studio Code](https://code.visualstudio.com/) terinstal.
- Di dalam VS Code, instal ekstensi berikut:
  - `Python` (dari Microsoft)
  - `PlatformIO IDE` (untuk pengembangan ESP32)
  - `Wokwi Simulator`

### Langkah-langkah Instalasi

Proyek ini dilengkapi dengan skrip `.bat` untuk mengotomatiskan seluruh proses. Cukup jalankan salah satu skrip (`run_dashboard.bat` atau `run_gui.bat`), dan skrip tersebut akan menangani pembuatan virtual environment dan instalasi semua package dari `requirements.txt` secara otomatis.

## Menjalankan Sensor Node (ESP32)

Ini adalah langkah pertama yang harus dilakukan agar ada data yang dikirim.

1.  Buka folder proyek ini di Visual Studio Code.
2.  Tekan `F1`, lalu ketik dan pilih **`Wokwi: Start Simulator`**.
3.  Biarkan tab simulator ini tetap berjalan di latar belakang.

_(Untuk alternatif menjalankan di browser, lihat bagian akhir dokumen ini.)_

---

## Cara Menjalankan Aplikasi

Setelah sensor berjalan, Anda dapat memilih salah satu dari tiga opsi berikut.

### Opsi 1: Visualisasi Web dengan Plotly & Dash (Direkomendasikan)

Metode ini akan menjalankan server web lokal yang menampilkan dasbor interaktif dengan data 50 sensor terakhir dan analisis tren sesaat.

- **Cara Otomatis (Windows)**:
  - Klik dua kali file **`run_dashboard.bat`**.
- **Cara Manual**:
  1.  Aktifkan virtual environment (`.venv\Scripts\activate`).
  2.  Jalankan perintah: `python src/dashboard.py`
  3.  Buka browser Anda dan kunjungi alamat **`http://127.0.0.1:8050/`**.

### Opsi 2: Visualisasi Desktop dengan Matplotlib & Tkinter

Metode ini akan membuka jendela aplikasi desktop sederhana yang menampilkan 50 data sensor terakhir.

- **Cara Otomatis (Windows)**:
  - Klik dua kali file **`run_gui.bat`**.
- **Cara Manual**:
  1.  Aktifkan virtual environment (`.\venv\Scripts\activate`).
  2.  Jalankan perintah: `python src/gui.py`

### Opsi 3: Analisis Data Historis

Gunakan skrip ini setelah Anda mengumpulkan data selama beberapa waktu (misalnya, beberapa jam atau hari). Skrip ini akan membaca **seluruh data** dari database dan menampilkan jendela grafik interaktif untuk analisis mendalam.

- **Cara Menjalankan**:
  1.  Pastikan aplikasi real-time (Opsi 1 atau 2) tidak sedang berjalan.
  2.  Buka terminal baru dan aktifkan virtual environment (`.\venv\Scripts\activate`).
  3.  Jalankan perintah:
      ```bash
      python src/analisis.py
      ```
  - Sebuah jendela akan muncul menampilkan dua plot: data mentah dan analisis tren suhu jangka panjang. Anda dapat menggunakan toolbar di jendela tersebut untuk men-zoom dan menggeser grafik.

---

## Informasi Tambahan

### Cara Mengakses Database SQLite

Semua data historis disimpan dalam file `climate_data.db`. Anda bisa membukanya menggunakan aplikasi gratis seperti **DB Browser for SQLite** ([sqlitebrowser.org](https://sqlitebrowser.org/dl/)) untuk melihat, memfilter, atau mengekspor data dalam format spreadsheet.

### Alternatif Menjalankan Wokwi (di Browser)

Jika Anda tidak menggunakan VS Code, Anda bisa menjalankan simulasi langsung di situs Wokwi.

1.  Buka [wokwi.com](https://wokwi.com/).
2.  Buat proyek baru dengan memilih template **ESP32**.
3.  Salin seluruh isi file **`main.cpp`** dari proyek ini dan tempelkan ke tab `sketch.cpp` di Wokwi.
4.  Salin seluruh isi file **`diagram.json`** dari proyek ini dan tempelkan ke tab `diagram.json` di Wokwi.
5.  Klik tombol **Start Simulation** (panah hijau).
