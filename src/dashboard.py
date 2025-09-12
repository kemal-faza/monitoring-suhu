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
import sys
import random

# --- KONFIGURASI ---
MQTT_BROKER = "broker.hivemq.com"
MQTT_TOPIC = "0013/climate"
DB_FILE = "climate_data.db"
CLIENT_ID = f"dashboard_client_iot_project_{random.randint(0, 10000)}"

# --- SETUP DATA ---
live_data = deque(maxlen=50) 
data_lock = threading.Lock()

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

# --- LOGIKA MQTT ---

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("MQTT Terhubung! Mengirim permintaan subscribe...")
        # Lakukan subscribe setelah koneksi berhasil
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Gagal terhubung ke MQTT, code: {reason_code}")

# DIAGNOSTIK 1: Tambahkan callback on_subscribe
def on_subscribe(client, userdata, mid, reason_codes, properties):
    # Cek apakah subscription berhasil (reason code < 128 berarti sukses)
    if reason_codes[0].is_failure:
        print(f"Gagal subscribe ke topik '{MQTT_TOPIC}'. Alasan: {reason_codes[0]}")
    else:
        print(f"Berhasil subscribe ke topik '{MQTT_TOPIC}'!")

def on_message(client, userdata, msg):
    # DIAGNOSTIK 2: Cetak pesan mentah SEGERA setelah diterima
    print(f"--> Pesan mentah diterima di topik '{msg.topic}': {msg.payload.decode()}")
    
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        temp = payload.get("temperature")
        hum = payload.get("humidity")
        ts = payload.get("ts", datetime.now().timestamp())
        dt_object = datetime.fromtimestamp(ts)

        if temp is not None and hum is not None:
            cursor = db_conn.cursor()
            cursor.execute("INSERT INTO climate (timestamp, temperature, humidity) VALUES (?, ?, ?)",
                           (dt_object.strftime("%Y-%m-%d %H:%M:%S"), temp, hum))
            db_conn.commit()
            
            with data_lock:
                live_data.append((dt_object, temp, hum))
            
    except Exception as e:
        print(f"Error memproses pesan: {e}")

# --- APLIKASI DASH (Tidak ada perubahan di sini) ---
app = dash.Dash(__name__)
# ... (sisa layout Dash sama persis)
app.title = "Climate Monitor"

app.layout = html.Div(style={'backgroundColor': '#282c34', 'color': '#FFFFFF', 'fontFamily': 'Arial, sans-serif', 'padding': '20px'}, children=[
    html.Div(className='header', children=[
        html.H1(children='Dashboard Monitoring Suhu & Kelembaban', style={'textAlign': 'center'}),
        html.P(children='Data sensor real-time dari ESP32 via MQTT', style={'textAlign': 'center', 'fontSize': '1.2em'})
    ]),
    
    html.Div(className='graph-container', style={'marginTop': '30px'}, children=[
        dcc.Graph(id='graph-suhu'),
        html.Hr(style={'borderColor': '#555'}),
        dcc.Graph(id='graph-kelembaban'),
    ]),

    dcc.Interval(
        id='interval-component',
        interval=1*1000,
        n_intervals=0
    )
])

@app.callback(
    [Output('graph-suhu', 'figure'),
     Output('graph-kelembaban', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(_):
    with data_lock:
        if not live_data:
            empty_fig = go.Figure().update_layout(
                title_text="Menunggu Data...",
                template='plotly_dark'
            )
            return empty_fig, empty_fig
        
        timestamps, temperatures, humidities = zip(*list(live_data))

    fig_suhu = go.Figure(
        data=[go.Scatter(x=list(timestamps), y=list(temperatures), mode='lines+markers', line=dict(color='#FF5733'))],
        layout=go.Layout(
            title='Grafik Suhu Real-time',
            yaxis_title='Suhu (°C)',
            template='plotly_dark',
            margin=dict(l=40, r=40, t=40, b=40)
        )
    )

    fig_kelembaban = go.Figure(
        data=[go.Scatter(x=list(timestamps), y=list(humidities), mode='lines+markers', line=dict(color='#33CFFF'))],
        layout=go.Layout(
            title='Grafik Kelembaban Real-time',
            xaxis_title='Waktu',
            yaxis_title='Kelembaban (%)',
            template='plotly_dark',
            margin=dict(l=40, r=40, t=40, b=40)
        )
    )

    return fig_suhu, fig_kelembaban


# --- JALANKAN SERVER DAN INISIALISASI MQTT ---
if __name__ == '__main__':
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, CLIENT_ID)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    # DIAGNOSTIK 1 (lanjutan): Daftarkan callback on_subscribe
    mqtt_client.on_subscribe = on_subscribe
    
    try:
        mqtt_client.connect(MQTT_BROKER, 1883)
    except Exception as e:
        print(f"Gagal terhubung ke broker MQTT: {e}")
        sys.exit(1)

    mqtt_client.loop_start()

    app.run(debug=True, use_reloader=False)