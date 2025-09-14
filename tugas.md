Tentu, saya akan membuatkan dokumen persiapan berdasarkan semua informasi yang telah Anda berikan. Dokumen ini dirancang agar ringkas, profesional, dan sesuai dengan poin-poin yang Anda butuhkan untuk tugas kuliah Anda.

---

### **Dokumen Perancangan Proyek: Sistem Monitoring Suhu dan Kelembapan Real-time Berbasis IoT**

**Mata Kuliah:** Internet of Things (IoT)
**Proyek:** Aplikasi Real-time Pengukur Suhu Lokal dengan ESP32

Dokumen ini menguraikan arsitektur, teknologi yang digunakan, dan alur kerja untuk proyek monitoring suhu dan kelembapan. Proyek ini bertujuan untuk membangun sistem _end-to-end_ yang fungsional, mulai dari akuisisi data sensor hingga visualisasi interaktif.

---

### **1. Topologi / Arsitektur End-to-End**

Arsitektur sistem dirancang sebagai alur data satu arah dari perangkat sensor ke antarmuka pengguna, dengan broker MQTT sebagai pusat komunikasi.

**Diagram Alur Sederhana:**
`[Sensor Node] -> [Broker MQTT] -> [Data Logger] -> [Database] -> [Visualisasi Dasbor]`

**Komponen Utama:**

- **Sensor Node (Publisher):** Sebuah mikrokontroler ESP32 yang terhubung ke sensor DHT22. Perangkat ini bertanggung jawab untuk membaca data suhu dan kelembapan, memformatnya ke dalam standar JSON, dan mengirimkannya secara periodik ke Broker MQTT.
- **Broker MQTT:** Menggunakan layanan cloud publik **HiveMQ (`broker.hivemq.com`)** sebagai perantara pesan. Broker ini menerima data dari Sensor Node dan meneruskannya ke setiap klien yang berlangganan (subscribe) pada topik yang relevan.
- **Data Logger (Subscriber):** Sebuah skrip Python yang berjalan di komputer lokal. Skrip ini berlangganan topik MQTT, menerima data JSON yang masuk, dan bertugas untuk menyimpan setiap data ke dalam database lokal.
- **Database:** Menggunakan **SQLite**, sebuah sistem database berbasis file yang ringan. Database ini berfungsi untuk menyimpan data historis (time-series) yang mencakup timestamp, suhu, dan kelembapan.
- **Visualisasi Dasbor:** Menggunakan platform **Grafana** yang berjalan di server lokal. Grafana terhubung langsung ke database SQLite untuk mengambil data dan menampilkannya dalam bentuk dasbor interaktif yang dapat diakses melalui browser.

---

### **2. Platform IoT yang Digunakan**

Proyek ini dibangun menggunakan kombinasi perangkat keras, perangkat lunak, dan protokol standar industri berikut:

- **Perangkat Keras (Hardware):**

  - Mikrokontroler: **ESP32 DevKitC V4**
  - Sensor: **DHT22** (sensor suhu dan kelembapan digital)

- **Protokol Komunikasi:**

  - **MQTT (Message Queuing Telemetry Transport):** Protokol publish-subscribe yang ringan dan efisien, ideal untuk komunikasi perangkat IoT.

- **Perangkat Lunak & Bahasa Pemrograman:**

  - **Sensor Node:** Kode ditulis dalam **C++** menggunakan **Arduino Framework**.
  - **Data Logger:** Skrip ditulis dalam **Python 3**.
  - **Penyimpanan Data:** **SQLite**.
  - **Platform Visualisasi:** **Grafana**.

- **Lingkungan Pengembangan:**
  - **Wokwi:** Untuk simulasi sirkuit dan kode ESP32 secara virtual.
  - **Visual Studio Code** dengan ekstensi **PlatformIO:** Untuk pengembangan, manajemen library, dan deployment kode ke perangkat ESP32 fisik.

---

### **3. Alur Data (Sensor ke Visualisasi)**

Aliran data dalam sistem ini berjalan melalui langkah-langkah sekuensial berikut:

1.  **Akuisisi Data:** ESP32 secara periodik (setiap 5 detik) membaca nilai suhu dan kelembapan dari sensor DHT22.
2.  **Pemformatan JSON:** Data mentah tersebut diformat ke dalam payload JSON yang terstruktur agar mudah diproses oleh sistem lain. Contoh: `{"temperature": 28.1, "humidity": 65.7}`.
3.  **Publikasi ke MQTT:** ESP32 (sebagai klien MQTT) mempublikasikan payload JSON ke topik **`0013/climate`** pada broker HiveMQ.
4.  **Penerimaan Pesan:** Skrip Python `gui.py`, yang terus berjalan di latar belakang dan berlangganan topik `0013/climate`, secara instan menerima pesan tersebut dari broker.
5.  **Penyimpanan ke Database:** Skrip Python mem-parsing data dari JSON, menambahkan stempel waktu (timestamp) saat ini, dan menyisipkan data lengkap (timestamp, suhu, kelembapan) sebagai baris baru ke dalam tabel `climate` di file database `climate_data.db`.
6.  **Query Data oleh Grafana:** Server Grafana, yang telah dikonfigurasi untuk terhubung ke database SQLite, secara berkala menjalankan query SQL untuk mengambil data terbaru atau data dalam rentang waktu tertentu.
7.  **Tampilan di Dasbor:** Data yang diambil oleh Grafana ditampilkan kepada pengguna melalui browser dalam bentuk panel visual seperti grafik time-series, gauge, dan statistik.

---

### **4. Penyimpanan & Visualisasi**

- **Penyimpanan (Storage):**
  Penyimpanan data historis menggunakan **SQLite** karena sifatnya yang _serverless_, ringan, dan berbasis file tunggal, sehingga sangat cocok untuk pengembangan lokal dan aplikasi skala kecil.

  - **File Database:** `climate_data.db`
  - **Struktur Tabel (`climate`):**
    - `id` (INTEGER, Primary Key)
    - `timestamp` (DATETIME)
    - `temperature` (REAL)
    - `humidity` (REAL)

- **Visualisasi (Visualization):**
  **Grafana** dipilih sebagai platform visualisasi karena kemampuannya yang kuat untuk membuat dasbor yang profesional dan interaktif dari berbagai sumber data, termasuk SQLite.
  - **Sumber Data:** Grafana terhubung ke file `climate_data.db` melalui plugin SQLite.
  - **Tipe Visualisasi:** Dasbor akan berisi beberapa panel, seperti:
    - **Grafik Time Series:** Untuk memantau tren perubahan suhu dan kelembapan dari waktu ke waktu.
    - **Gauge:** Untuk menampilkan nilai suhu dan kelembapan terkini secara jelas.
    - **Stat Panel:** Untuk menunjukkan nilai tunggal penting seperti suhu rata-rata atau kelembapan tertinggi hari ini.

---

### **5. Alerting & Otomasi (Rencana Pengembangan)**

Fitur alerting dan otomasi belum diimplementasikan pada fase awal proyek ini, namun telah direncanakan sebagai pengembangan di masa depan untuk meningkatkan fungsionalitas sistem.

- **Rencana Alerting:**
  Mekanisme peringatan akan diimplementasikan menggunakan fitur **Grafana Alerts**. Sebuah aturan akan dibuat untuk memicu peringatan jika data sensor melebihi ambang batas yang ditentukan (misalnya, suhu di atas 35°C). Peringatan ini dapat dikonfigurasi untuk mengirim notifikasi melalui email atau platform pesan seperti Telegram.

- **Rencana Otomasi:**
  Sebagai pengembangan lebih lanjut, sistem dapat dilengkapi dengan kemampuan otomasi. Contohnya:
  1.  Ketika skrip Python mendeteksi suhu melebihi ambang batas, ia tidak hanya menyimpan data, tetapi juga mempublikasikan pesan perintah ke topik MQTT baru (cth: `0013/control`).
  2.  ESP32 akan dibuat untuk berlangganan topik `0013/control`.
  3.  Saat menerima pesan perintah (misal: `{"fan": "ON"}`), ESP32 akan mengaktifkan sebuah relay yang terhubung ke kipas pendingin. Ini menciptakan sebuah sistem loop tertutup yang reaktif.
