# Proyek Monitoring Suhu dan Kelembapan Berbasis IoT

Proyek ini adalah implementasi sistem _Internet of Things_ (IoT) _end-to-end_ sederhana untuk memonitor data suhu dan kelembapan secara _real-time_. Data dari sensor dikirim melalui protokol MQTT, disimpan dalam database lokal, dan dapat divisualisasikan melalui dasbor.

## 1. Topologi / Arsitektur End-to-End

Sistem ini terdiri dari beberapa komponen utama yang saling terhubung untuk membentuk alur data dari sensor fisik hingga ke antarmuka pengguna.

Arsitekturnya adalah sebagai berikut:

-   **Sensor Node (Publisher)**: Sebuah board ESP32 yang terhubung dengan sensor DHT22. Bertugas membaca data, memformatnya ke dalam JSON, dan mengirimkannya ke Broker MQTT.
-   **Broker MQTT**: Menggunakan layanan cloud publik **HiveMQ** sebagai perantara pesan. Ini adalah pusat komunikasi yang menghubungkan publisher (ESP32) dan subscriber (skrip Python).
-   **Data Logger (Subscriber)**: Sebuah skrip Python yang berjalan di komputer lokal. Bertugas untuk berlangganan (subscribe) ke topic MQTT, menerima data, dan menyimpannya ke dalam database.
-   **Database**: Menggunakan **SQLite**, sebuah database berbasis file yang ringan untuk menyimpan data historis suhu dan kelembapan.
-   **Visualisasi**: Menggunakan **Grafana** untuk membuat dasbor interaktif yang membaca data langsung dari database SQLite.

---

## 2. Platform IoT yang Digunakan

Proyek ini dibangun menggunakan kombinasi hardware, software, dan protokol berikut:

-   **Hardware**:
    -   Mikrokontroler: **ESP32 DevKitC V4**
    -   Sensor: **DHT22** (untuk suhu dan kelembapan)
-   **Protokol Komunikasi**: **MQTT**
-   **Broker MQTT**: **HiveMQ Public Broker** (`broker.hivemq.com`)
-   **Bahasa Pemrograman**:
    -   Sensor Node: **C++** dengan **Arduino Framework**
    -   Data Logger: **Python 3**
-   **Penyimpanan Data**: **SQLite**
-   **Lingkungan Simulasi & Pengembangan**:
    -   **Wokwi** (untuk simulasi hardware ESP32)
    -   **Visual Studio Code** + **PlatformIO** (untuk pengembangan dan upload kode ke ESP32 fisik)
-   **Visualisasi**: **Grafana**

---

## 3. Alur Data (Sensor ke Visualisasi)

Aliran data dalam sistem ini berjalan secara sekuensial melalui beberapa tahapan:

1.  **Pengambilan Data**: ESP32 membaca data suhu dan kelembapan dari sensor DHT22 setiap 5 detik.
2.  **Pemformatan Data**: Data mentah diformat ke dalam sebuah payload **JSON** agar terstruktur. Contoh: `{"temperature": 25.5, "humidity": 60.2}`.
3.  **Publikasi (Publish)**: ESP32, yang berperan sebagai klien MQTT, mempublikasikan (mengirim) data JSON ke topic **`0013/climate`** di broker HiveMQ.
4.  **Penerimaan (Subscribe)**: Skrip Python `gui.py` yang berjalan di komputer lokal sudah berlangganan ke topic `0013/climate`. Ia akan langsung menerima data JSON yang dikirim oleh ESP32.
5.  **Penyimpanan**: Setelah menerima data, skrip Python akan mem-parsing JSON, menambahkan _timestamp_, dan menyimpan data suhu dan kelembapan ke dalam tabel `climate` di database SQLite (`climate_data.db`).
6.  **Visualisasi**: Server Grafana yang berjalan di komputer lokal dikonfigurasi untuk terhubung ke file database SQLite.
7.  **Tampilan**: Grafana secara periodik mengirimkan query SQL ke database untuk mengambil data terbaru dan menampilkannya dalam bentuk grafik _time-series_, _gauge_, atau panel statistik lainnya di dasbor yang bisa diakses melalui browser.

---

## 4. Penyimpanan & Visualisasi

### Penyimpanan (Storage)

Penyimpanan data historis menggunakan **SQLite**, sebuah sistem manajemen database yang ringan, berbasis file, dan tidak memerlukan server terpisah. Ini membuatnya ideal untuk aplikasi skala kecil hingga menengah dan pengembangan lokal.

-   **File Database**: `climate_data.db`
-   **Struktur Tabel**: `climate`
    -   `id`: INTEGER (Primary Key)
    -   `timestamp`: DATETIME (Waktu data disimpan)
    -   `temperature`: REAL (Nilai suhu dalam Celcius)
    -   `humidity`: REAL (Nilai kelembapan dalam %)

### Visualisasi (Visualization)

Untuk visualisasi, **Grafana** adalah platform yang direkomendasikan. Grafana memungkinkan pembuatan dasbor yang kaya fitur dan interaktif.

-   **Sumber Data**: Grafana terhubung langsung ke file `climate_data.db` menggunakan plugin SQLite.
-   **Contoh Panel**:
    -   **Grafik Time Series**: Menampilkan tren suhu dan kelembapan dari waktu ke waktu.
    -   **Gauge**: Menampilkan nilai suhu dan kelembapan terkini secara visual.
    -   **Stat Panel**: Menampilkan nilai agregat seperti suhu tertinggi/terendah dalam 24 jam terakhir.

---

## 5. Cara Setup

Berikut adalah langkah-langkah untuk menjalankan keseluruhan proyek ini di lingkungan lokal.

### Prasyarat

-   **Visual Studio Code** dengan ekstensi **PlatformIO IDE** terinstal.
-   **Python 3** terinstal di komputer.
-   Akses internet.
-   **Grafana** terinstal di komputer.

### Langkah-langkah

1.  **Setup Backend (Python Logger)**

    -   Buka terminal atau CMD.
    -   Buat dan aktifkan sebuah virtual environment Python di dalam folder proyek untuk menjaga dependensi tetap bersih.
        ```bash
        # Membuat virtual environment
        python -m venv .venv
        # Mengaktifkan di Windows
        .\.venv\Scripts\activate
        # Mengaktifkan di macOS/Linux
        # source .venv/bin/activate
        ```
    -   Instal library yang dibutuhkan:
        ```bash
        pip install paho-mqtt
        ```
    -   Jalankan skrip logger. Biarkan terminal ini tetap berjalan di latar belakang.
        ```bash
        python gui.py
        ```
    -   Kamu akan melihat pesan "Berhasil terhubung ke Broker MQTT!" jika koneksi berhasil.

2.  **Setup Sensor Node (ESP32)**

    -   Buka folder proyek ini menggunakan Visual Studio Code.
    -   PlatformIO akan secara otomatis mendeteksi file `platformio.ini` dan menginstal _toolchain_ serta library yang diperlukan.
    -   Mulai simulasi dengan menekan `F1` dan memilih `Wokwi: Start Simulator`.
    -   Kode akan otomatis berjalan di ESP32 virtual.

3.  **Verifikasi Alur Data**

    -   Perhatikan output di terminal tempat skrip `gui.py` berjalan. Kamu akan melihat data suhu dan kelembapan baru dicatat setiap beberapa detik, yang menandakan seluruh alur dari sensor ke database sudah berfungsi.

4.  **Setup Visualisasi (Grafana)**

# Panduan Lengkap Setup Grafana untuk Proyek IoT

Dokumen ini berisi panduan langkah demi langkah untuk menginstal, mengkonfigurasi, dan memvisualisasikan data sensor dari database SQLite menggunakan Grafana di lingkungan Windows.

---

## Langkah 1: Menginstal Grafana

Langkah pertama adalah mengunduh dan menginstal aplikasi Grafana di komputer.

1.  **Unduh Installer**: Buka halaman unduhan resmi Grafana di **[https://grafana.com/grafana/download](https://grafana.com/grafana/download)**.
2.  Pilih versi **terbaru** dan sistem operasi **Windows**.
3.  Klik tombol **Download the installer**.
4.  Jalankan file `.msi` yang sudah diunduh. Proses instalasi sangat standar, cukup klik **"Next"** beberapa kali seperti menginstal aplikasi Windows pada umumnya.

---

## Langkah 2: Menjalankan dan Mengakses Server Grafana

Setelah instalasi, server Grafana akan berjalan otomatis sebagai layanan (service) di latar belakang.

1.  **Buka Browser**: Buka browser web (Chrome, Firefox, dll.).
2.  **Akses Alamat Grafana**: Ketik alamat berikut di address bar:
    ```
    http://localhost:3000
    ```
3.  **Login**: Gunakan kredensial default untuk login pertama kali:
    -   **Username**: `admin`
    -   **Password**: `admin`
4.  **Ubah Password**: Grafana akan memintamu untuk membuat password baru yang lebih aman.

> **Troubleshooting**: Jika halaman tidak bisa diakses, buka aplikasi **"Services"** di Windows, cari layanan **"Grafana"**, klik kanan, dan pilih **"Start"**.

---

## Langkah 3: Menginstal Plugin SQLite

Plugin ini wajib diinstal agar Grafana bisa membaca file database `.db` milikmu.

1.  **Buka CMD sebagai Administrator**:

    -   Klik tombol **Windows**, ketik `cmd`.
    -   Pada hasil pencarian **"Command Prompt"**, klik kanan, lalu pilih **"Run as administrator"**.

2.  **Pindah ke Direktori `bin` Grafana**:

    ```cmd
    cd "C:\Program Files\GrafanaLabs\grafana\bin"
    ```

3.  **Jalankan Perintah Instalasi**:

    ```cmd
    grafana-cli plugins install frser-sqlite-datasource
    ```

4.  **Restart Server Grafana (Wajib)**:
    -   Buka kembali aplikasi **"Services"**.
    -   Cari **"Grafana"**, klik kanan, dan pilih **"Restart"**.

---

## Langkah 4: Menambahkan SQLite sebagai Sumber Data (Data Source)

Sekarang kita akan menghubungkan Grafana ke file `climate_data.db`.

1.  Buka dasbor Grafana di `http://localhost:3000` dan login.
2.  Di menu sebelah kiri, klik ikon gerigi (⚙️ **Administration**) lalu pilih **Data sources**.
3.  Klik tombol biru **"Add new data source"**.
4.  Di kolom pencarian, ketik `SQLite` dan pilih.
5.  **Konfigurasi Path**:
    -   **Name**: Beri nama yang mudah diingat, misalnya `Database Suhu Lokal`.
    -   **Path**: Masukkan **path lengkap (absolut)** ke file `climate_data.db`.
        > Contoh: `C:\Users\NamaUser\Documents\ProyekIoT\climate_data.db`.
        > _Tips: Untuk mendapatkan path lengkap, cari file-nya di File Explorer, tahan tombol `Shift` lalu klik kanan pada file, dan pilih "Copy as path"._
6.  **Simpan & Tes**: Gulir ke bawah dan klik tombol **"Save & test"**. Kamu akan melihat notifikasi hijau bertuliskan "Data source is working" jika berhasil.

---

## Langkah 5: Membuat Panel dan Memvisualisasikan Data

Ini adalah langkah terakhir untuk menampilkan data dalam bentuk grafik.

1.  Di menu kiri, klik ikon plus (➕ **New**) dan pilih **New Dashboard**.
2.  Klik tombol **"Add visualization"**.
3.  **Pilih Sumber Data**: Di bagian bawah, pastikan dropdown **"Data source"** sudah memilih `Database Suhu Lokal`.
4.  **Tulis Query SQL**: Di bawahnya, klik tombol **"</> Query"** untuk beralih ke mode teks dan masukkan query berikut:
    ```sql
    SELECT
      CAST(strftime('%s', timestamp) AS INT) * 1000 AS "time",
      temperature,
      humidity
    FROM climate
    ORDER BY "time" ASC
    ```
5.  **Atur Format**: Di sebelah kanan query, pastikan opsi **Format** diatur sebagai **Time series**.
6.  Grafik akan otomatis muncul di bagian atas.
7.  **Kustomisasi**: Di panel kanan (Panel options), beri **Title** pada panelmu, misalnya "Tren Suhu & Kelembapan".
8.  **Simpan**: Klik tombol **"Apply"** di pojok kanan atas untuk menyimpan panel, lalu klik ikon disket (💾) untuk menyimpan keseluruhan dasbor.
