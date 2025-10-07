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
MQTT_TOPIC = "Informatika/IoT-E/Kelompok9/multi_node/+"
DB_FILE = "climate_data.db"
CLIENT_ID = f"dashboard_client_iot_project_{random.randint(0, 10000)}"

# --- THRESHOLD PERINGATAN ---
TEMP_LOW = 15.0
TEMP_HIGH = 30.0  # >30 dianggap tinggi
TEMP_VERY_HIGH = 40.0  # >40 dianggap sangat tinggi (opsional)
HUM_LOW = 30.0
HUM_HIGH = 70.0

# --- SETUP DATA ---
live_data = deque(maxlen=50)
data_lock = threading.Lock()


def setup_database():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS climate (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL
        )"""
    )
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
    if reason_codes[0] >= 128:
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
        ts = float(payload.get("ts", datetime.now().timestamp()))
        dt_object = datetime.fromtimestamp(ts)

        if temp is not None and hum is not None:
            cursor = db_conn.cursor()
            cursor.execute(
                "INSERT INTO climate (timestamp, temperature, humidity) VALUES (?, ?, ?)",
                (dt_object.strftime("%Y-%m-%d %H:%M:%S"), temp, hum),
            )
            db_conn.commit()

            with data_lock:
                live_data.append((dt_object, temp, hum))

    except Exception as e:
        print(f"Error memproses pesan: {e}")


# --- APLIKASI DASH (Tidak ada perubahan di sini) ---
app = dash.Dash(__name__)
# ... (sisa layout Dash sama persis)
app.title = "Climate Monitor"

app.layout = html.Div(
    style={
        "backgroundColor": "#282c34",
        "color": "#FFFFFF",
        "fontFamily": "Arial, sans-serif",
        "padding": "20px",
    },
    children=[
        html.Div(
            className="header",
            children=[
                html.H1(
                    children="Dashboard Monitoring Suhu & Kelembaban",
                    style={"textAlign": "center"},
                ),
                html.P(
                    children="Data sensor real-time dari ESP32 via MQTT",
                    style={"textAlign": "center", "fontSize": "1.2em"},
                ),
            ],
        ),
        html.Div(
            id="alert-container",
            style={
                "marginTop": "15px",
                "padding": "12px 18px",
                "backgroundColor": "#20232a",
                "border": "1px solid #444",
                "borderRadius": "6px",
                "fontWeight": "bold",
                "fontSize": "15px",
                "minHeight": "48px",
            },
            children="Menunggu data sensor...",
        ),
        html.Div(
            className="graph-container",
            style={"marginTop": "30px"},
            children=[
                dcc.Graph(id="graph-suhu"),
                html.Hr(style={"borderColor": "#555"}),
                dcc.Graph(id="graph-kelembaban"),
            ],
        ),
        dcc.Interval(id="interval-component", interval=1 * 1000, n_intervals=0),
    ],
)


@app.callback(
    [
        Output("alert-container", "children"),
        Output("graph-suhu", "figure"),
        Output("graph-kelembaban", "figure"),
    ],
    [Input("interval-component", "n_intervals")],
)
def update_graphs(_):
    with data_lock:
        if not live_data:
            empty_fig = go.Figure().update_layout(
                title_text="Menunggu Data...", template="plotly_dark"
            )
            return (
                "Menunggu data sensor...",
                empty_fig,
                empty_fig,
            )

        timestamps, temperatures, humidities = zip(*live_data)
        last_ts, last_temp, last_hum = timestamps[-1], temperatures[-1], humidities[-1]

    # --- Logika peringatan ---
    alerts = []

    # Suhu
    if last_temp < TEMP_LOW:
        alerts.append(
            html.Span(
                f"Peringatan: Suhu RENDAH ({last_temp:.1f} °C)",
                style={"color": "#33CFFF", "marginRight": "18px"},
            )
        )
    elif last_temp >= TEMP_VERY_HIGH:
        alerts.append(
            html.Span(
                f"BAHAYA: Suhu SANGAT TINGGI ({last_temp:.1f} °C)",
                style={"color": "#ff3333", "marginRight": "18px"},
            )
        )
    elif last_temp > TEMP_HIGH:
        alerts.append(
            html.Span(
                f"Peringatan: Suhu TINGGI ({last_temp:.1f} °C)",
                style={"color": "#FF8800", "marginRight": "18px"},
            )
        )
    else:
        alerts.append(
            html.Span(
                f"Suhu Normal ({last_temp:.1f} °C)",
                style={"color": "#55dd55", "marginRight": "18px"},
            )
        )

    # Kelembaban
    if last_hum < HUM_LOW:
        alerts.append(
            html.Span(
                f"Kelembaban RENDAH ({last_hum:.1f} %)",
                style={"color": "#ffa500", "marginRight": "18px"},
            )
        )
    elif last_hum > HUM_HIGH:
        alerts.append(
            html.Span(
                f"Kelembaban TINGGI ({last_hum:.1f} %)",
                style={"color": "#ffcc00", "marginRight": "18px"},
            )
        )
    else:
        alerts.append(
            html.Span(
                f"Kelembaban Normal ({last_hum:.1f} %)",
                style={"color": "#55ddaa", "marginRight": "18px"},
            )
        )

    alert_container = html.Div(
        children=alerts
        + [
            html.Span(
                f"Terakhir: {last_ts.strftime('%H:%M:%S')}",
                style={"color": "#888", "marginLeft": "12px", "fontWeight": "normal"},
            )
        ]
    )

    # --- Grafik (tidak berubah) ---
    fig_suhu = go.Figure(
        data=[
            go.Scatter(
                x=list(timestamps),
                y=list(temperatures),
                mode="lines+markers",
                line=dict(color="#FF5733"),
            )
        ],
        layout=go.Layout(
            title="Grafik Suhu Real-time",
            yaxis_title="Suhu (°C)",
            template="plotly_dark",
            margin=dict(l=40, r=40, t=40, b=40),
        ),
    )

    fig_kelembaban = go.Figure(
        data=[
            go.Scatter(
                x=list(timestamps),
                y=list(humidities),
                mode="lines+markers",
                line=dict(color="#33CFFF"),
            )
        ],
        layout=go.Layout(
            title="Grafik Kelembaban Real-time",
            xaxis_title="Waktu",
            yaxis_title="Kelembaban (%)",
            template="plotly_dark",
            margin=dict(l=40, r=40, t=40, b=40),
        ),
    )

    return alert_container, fig_suhu, fig_kelembaban


# --- JALANKAN SERVER DAN INISIALISASI MQTT ---
if __name__ == "__main__":
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
