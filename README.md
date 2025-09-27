# Proyek Monitoring Suhu dan Kelembapan Real-time Berbasis IoT

Selamat datang di proyek monitoring IoT _end-to-end_. Sistem ini dirancang untuk mengambil data suhu dan kelembapan dari sensor, mengirimkannya melalui protokol MQTT, menyimpannya dalam database, dan menampilkannya secara _real-time_ melalui dua opsi visualisasi: **dasbor web interaktif** (Plotly & Dash) atau **aplikasi desktop sederhana** (Matplotlib & Tkinter).

## Fitur Utama

-   **Monitoring Real-time**: Lihat data suhu dan kelembapan saat itu juga.
-   **Pencatatan Data Historis**: Semua data sensor disimpan dalam database lokal SQLite untuk analisis di kemudian hari.
-   **Dua Opsi Visualisasi**:
    1.  **Dasbor Web (Direkomendasikan)**: Antarmuka modern, interaktif, dan dapat diakses melalui browser, dibangun dengan Plotly & Dash.
    2.  **Aplikasi Desktop**: Jendela aplikasi sederhana yang ringan dan berjalan secara native di OS Anda, dibangun dengan Matplotlib & Tkinter.
-   **Arsitektur Berbasis MQTT**: Menggunakan protokol MQTT yang ringan dan efisien, standar industri untuk komunikasi IoT.
-   **Simulasi Hardware**: Proyek ini dapat dijalankan sepenuhnya menggunakan simulator Wokwi, tanpa memerlukan perangkat keras fisik.

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

    subgraph "Visualisasi (Pilih Salah Satu)"
        F[Opsi 1: Dashboard Web (Dash)] -->|Membaca Data| E;
        G[Opsi 2: Aplikasi Desktop (Matplotlib)] -->|Membaca Data| E;
    end

    B -->|Publish ke Topik '0013/climate'| C;
    C -->|Subscribe ke Topik '0013/climate'| D;
```

## Teknologi yang Digunakan

-   **Hardware / Simulasi**:
    -   Mikrokontroler: **ESP32 DevKitC V4**
    -   Sensor: **DHT22** (suhu dan kelembapan)
    -   Simulator: **Wokwi**
-   **Protokol Komunikasi**: **MQTT**
-   **Broker MQTT**: **HiveMQ Public Broker** (`broker.hivemq.com`)
-   **Backend & Penyimpanan**:
    -   Bahasa: **Python 3**
    -   Database: **SQLite**
-   **Frontend / Visualisasi**:
    -   **Opsi 1**: **Plotly & Dash** (untuk dasbor web)
    -   **Opsi 2**: **Matplotlib & Tkinter** (untuk aplikasi desktop)
-   **Lingkungan Pengembangan**:
    -   **Visual Studio Code** + Ekstensi **PlatformIO** & **Python**.

## Struktur Folder

```
proyek-monitoring-suhu/
├── src/
│   ├── dashboard.py         # Backend & Frontend untuk versi Plotly/Dash
│   ├── gui.py               # Backend & Frontend untuk versi Matplotlib/Tkinter
│   ├── main.cpp             # Kode firmware untuk ESP32
│   └── diagram.json         # Konfigurasi sirkuit untuk Wokwi
├── .venv/                   # Folder virtual environment (dibuat otomatis)
├── requirements.txt         # Daftar semua package Python yang dibutuhkan
├── run_dashboard.bat        # Skrip untuk menjalankan versi Plotly/Dash
└── run_gui.bat              # Skrip untuk menjalankan versi Matplotlib/Tkinter
```

## Panduan Setup (Wajib Dilakukan Pertama Kali)

Sebelum menjalankan aplikasi, Anda perlu menyiapkan lingkungan pengembangan.

### Prasyarat

-   [Python 3.8+](https://www.python.org/downloads/) terinstal. Pastikan untuk mencentang "Add Python to PATH" saat instalasi.
-   [Visual Studio Code](https://code.visualstudio.com/) terinstal.
-   Di dalam VS Code, instal ekstensi berikut:
    -   `Python` (dari Microsoft)
    -   `PlatformIO IDE` (untuk pengembangan ESP32)
    -   `Wokwi Simulator`

### Langkah-langkah Instalasi

Proyek ini dilengkapi dengan skrip `.bat` untuk mengotomatiskan seluruh proses. Cukup jalankan skrip yang sesuai dengan visualisasi yang ingin Anda coba, dan skrip tersebut akan menangani pembuatan virtual environment dan instalasi package secara otomatis.

## Cara Menjalankan Aplikasi

Pastikan Anda sudah menjalankan **Sensor Node (ESP32)** terlebih dahulu (lihat panduan di bawah). Setelah itu, pilih salah satu dari dua opsi visualisasi berikut:

---

### Opsi 1: Visualisasi Web dengan Plotly & Dash (Direkomendasikan)

Metode ini akan menjalankan server web lokal. Anda akan melihat dasbor melalui browser.

-   **Cara Otomatis (Windows)**:
    -   Klik dua kali file **`run_dashboard.bat`**.
-   **Cara Manual**:
    1.  Aktifkan virtual environment (`.venv\Scripts\activate`).
    2.  Jalankan perintah: `python src/dashboard.py`
    3.  Buka browser Anda dan kunjungi alamat **`http://127.0.0.1:8050/`**.

---

### Opsi 2: Visualisasi Desktop dengan Matplotlib & Tkinter

Metode ini akan membuka jendela aplikasi desktop secara langsung.

-   **Cara Otomatis (Windows)**:
    -   Klik dua kali file **`run_gui.bat`**.
-   **Cara Manual**:
    1.  Aktifkan virtual environment (`.\venv\Scripts\activate`).
    2.  Jalankan perintah: `python src/gui.py`

---

## Menjalankan Sensor Node (ESP32)

Ini adalah langkah pertama yang harus dilakukan. Anda bisa menjalankannya melalui simulasi di Wokwi.

### Opsi A: Menggunakan Wokwi di VS Code (Lokal)

1.  Buka folder proyek ini di Visual Studio Code.
2.  Tunggu PlatformIO selesai menginisialisasi proyek.
3.  Tekan `F1`, lalu ketik dan pilih **`Wokwi: Start Simulator`**.
4.  Simulator akan terbuka di tab baru dan kode `main.cpp` akan otomatis berjalan.

### Opsi B: Menggunakan Wokwi di Browser (Cloud)

Jika Anda tidak menggunakan VS Code, Anda bisa menjalankan simulasi langsung di situs Wokwi.

1.  Buka [wokwi.com](https://wokwi.com/).
2.  Buat proyek baru dengan memilih template **ESP32**.
3.  Salin seluruh isi file **`main.cpp`** dari proyek ini dan tempelkan ke tab `sketch.cpp` di Wokwi.
4.  Salin seluruh isi file **`diagram.json`** dari proyek ini dan tempelkan ke tab `diagram.json` di Wokwi.
5.  Klik tombol **Start Simulation** (panah hijau).
