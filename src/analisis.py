import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

DB_FILE = "climate_data.db"
# Konfigurasi untuk Moving Average (Rata-rata Bergerak)
MOVING_AVG_WINDOW = 12 

try:
    # --- 1. MEMBACA DATA DARI DATABASE ---
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM climate", conn, 
                           parse_dates=['timestamp'], 
                           index_col='timestamp')
    print(f"Berhasil membaca {len(df)} baris data dari '{DB_FILE}'.")

except Exception as e:
    print(f"Gagal membaca database: {e}")
    exit()
finally:
    if conn:
        conn.close()

if df.empty:
    print("Tidak ada data untuk dianalisis.")
    exit()

# --- 2. PERHITUNGAN ANALISIS ---
# Menghitung Suhu Mulus (Moving Average)
df['smoothed_temperature'] = df['temperature'].rolling(window=MOVING_AVG_WINDOW).mean()

# Menghitung Garis Tren (Linear Regression)
x_numeric = (df.index - df.index[0]).total_seconds().values
y_values = df['temperature'].values
slope, intercept = np.polyfit(x_numeric, y_values, 1)
df['trend_line'] = slope * x_numeric + intercept

# --- 3. VISUALISASI DATA (DALAM SATU JENDELA) ---

# Buat satu Figure (jendela) yang berisi 2 subplot (area plot)
# nrows=2, ncols=1 berarti 2 baris, 1 kolom
# figsize=(15, 10) membuat jendela lebih tinggi untuk mengakomodasi 2 plot
# sharex=True adalah kunci untuk membuat zoom/pan terhubung
fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(15, 10), sharex=True)

# Mengatur judul utama untuk keseluruhan jendela
fig.suptitle('Analisis Data Historis Suhu & Kelembaban', fontsize=16)

# a) Plot Pertama (Atas): Data Mentah
ax1.plot(df.index, df['temperature'], label='Suhu (Mentah)', color='red', alpha=0.7)
ax1.plot(df.index, df['humidity'], label='Kelembaban (Mentah)', color='blue', alpha=0.7)
ax1.set_title('Data Sensor Mentah')
ax1.set_ylabel('Nilai')
ax1.legend()
ax1.grid(True)
# Label sumbu-x di plot atas otomatis disembunyikan karena sharex=True

# b) Plot Kedua (Bawah): Analisis Suhu
ax2.plot(df.index, df['temperature'], label='Suhu (Mentah)', color='gray', linestyle=':', alpha=0.5)
ax2.plot(df.index, df['smoothed_temperature'], label=f'Suhu Mulus (Moving Avg)', color='green', linewidth=2.5)
ax2.plot(df.index, df['trend_line'], label='Garis Tren Jangka Panjang', color='yellow', linestyle='--', linewidth=2.5)
ax2.set_title('Analisis Tren Suhu')
ax2.set_xlabel('Waktu')
ax2.set_ylabel('Suhu (°C)')
ax2.legend()
ax2.grid(True)

# Merapikan layout agar tidak ada yang tumpang tindih
fig.tight_layout(rect=[0, 0.03, 1, 0.95]) # rect menyesuaikan posisi agar suptitle tidak tumpang tindih

# Tampilkan plot
plt.show()

print("\n--- Analisis Selesai ---")
print(f"Kemiringan (Slope) Garis Tren: {slope:.6f}")
if slope > 0:
    print("Interpretasi: Secara umum, tren suhu menunjukkan PENINGKATAN.")
elif slope < 0:
    print("Interpretasi: Secara umum, tren suhu menunjukkan PENURUNAN.")
else:
    print("Interpretasi: Secara umum, tren suhu STABIL.")