import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import paho.mqtt.client as mqtt
import sqlite3
import json
from datetime import datetime
import threading
from collections import deque

# --- KONFIGURASI ---
MQTT_BROKER = "broker.hivemq.com"
MQTT_TOPIC = "0013/climate"
DB_FILE = "climate_data.db"

# --- SETUP DATA & KONEKSI ---

# Deque adalah list dengan ukuran maksimal, cocok untuk menyimpan data terbaru di memori
# Menyimpan (timestamp, temperature, humidity)
live_data = deque(maxlen=50) 
# Kunci (Lock) untuk memastikan data tidak rusak saat diakses oleh thread berbeda
data_lock = threading.Lock()

# Fungsi untuk setup dan koneksi database
def setup_database():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS climate (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL
        )""")
    conn.commit()
    print(f"Database '{DB_FILE}' siap.")
    return conn

db_conn = setup_database()

# --- LOGIKA MQTT (BERJALAN DI BACKGROUND) ---

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT Terhubung!")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Gagal terhubung ke MQTT, code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        temp = payload.get("temperature")
        hum = payload.get("humidity")
        ts = payload.get("ts", datetime.now().timestamp())
        dt_object = datetime.fromtimestamp(ts)

        if temp is not None and hum is not None:
            # 1. Simpan ke database
            cursor = db_conn.cursor()
            cursor.execute("INSERT INTO climate (timestamp, temperature, humidity) VALUES (?, ?, ?)",
                           (dt_object.strftime("%Y-%m-%d %H:%M:%S"), temp, hum))
            db_conn.commit()
            
            # 2. Simpan ke deque untuk live update (gunakan lock)
            with data_lock:
                live_data.append((dt_object, temp, hum))
            
            print(f"Data diterima: {dt_object} - Temp: {temp}°C, Hum: {hum}%")

    except Exception as e:
        print(f"Error memproses pesan: {e}")

# Inisialisasi dan jalankan client MQTT di thread terpisah
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "dashboard_client")
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, 1883)
# loop_start() menjalankan listener di background thread, tidak memblokir server Dash
mqtt_client.loop_start()

# --- APLIKASI DASH (FRONTEND & SERVER) ---

# Inisialisasi aplikasi Dash
app = dash.Dash(__name__)

# Mendefinisikan struktur/layout halaman web
app.layout = html.Div(style={'backgroundColor': '#f0f0f0', 'fontFamily': 'Arial, sans-serif'}, children=[
    html.H1(
        children='Dashboard Monitoring Suhu & Kelembaban',
        style={'textAlign': 'center', 'color': '#333'}
    ),
    
    html.Div(children='Data sensor real-time dari ESP32.', style={'textAlign': 'center', 'color': '#555'}),

    # Komponen Grafik Suhu
    dcc.Graph(id='graph-suhu'),
    
    # Komponen Grafik Kelembaban
    dcc.Graph(id='graph-kelembaban'),

    # Komponen Interval: Pemicu tak terlihat yang akan mengupdate grafik setiap 1 detik
    dcc.Interval(
        id='interval-component',
        interval=1*1000,  # dalam milidetik
        n_intervals=0
    )
])

# Callback: "Jantung" dari aplikasi Dash yang membuatnya interaktif
# Fungsi ini akan dijalankan setiap kali 'interval-component' berdetak
@app.callback(
    [Output('graph-suhu', 'figure'),
     Output('graph-kelembaban', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(n):
    # Salin data dengan aman menggunakan lock
    with data_lock:
        if not live_data:
            # Jika tidak ada data, kembalikan grafik kosong
            empty_fig = go.Figure().update_layout(title_text="Menunggu Data...", xaxis_title="Waktu", yaxis_title="Nilai")
            return empty_fig, empty_fig
        
        # Unzip data dari deque ke list terpisah
        timestamps, temperatures, humidities = zip(*list(live_data))

    # Buat figure untuk Suhu
    fig_suhu = go.Figure(
        data=[go.Scatter(x=list(timestamps), y=list(temperatures), mode='lines+markers', line=dict(color='red'))],
        layout=go.Layout(
            title='Grafik Suhu Real-time',
            xaxis_title='Waktu',
            yaxis_title='Suhu (°C)',
            template='plotly_white'
        )
    )

    # Buat figure untuk Kelembaban
    fig_kelembaban = go.Figure(
        data=[go.Scatter(x=list(timestamps), y=list(humidities), mode='lines+markers', line=dict(color='blue'))],
        layout=go.Layout(
            title='Grafik Kelembaban Real-time',
            xaxis_title='Waktu',
            yaxis_title='Kelembaban (%)',
            template='plotly_white'
        )
    )

    return fig_suhu, fig_kelembaban

# --- Jalankan Server ---
if __name__ == '__main__':
    # debug=True memungkinkan hot-reloading (server otomatis restart jika ada perubahan kode)
    app.run(debug=True)