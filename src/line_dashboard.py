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
# Ganti topik wildcard dengan list node yang diizinkan
ALLOWED_NODES = ["node_001", "node_002"]  # Hanya node ini yang diizinkan
MQTT_TOPIC_BASE = "Informatika/IoT-E/Kelompok9/multi_node"
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
            node_id TEXT NOT NULL,
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

        # Subscribe ke setiap node yang diizinkan
        for node_id in ALLOWED_NODES:
            topic = f"{MQTT_TOPIC_BASE}/{node_id}"
            result = client.subscribe(topic)
            print(f"Subscribe to {topic} - Result: {result}")

        print(f"Listening to nodes: {ALLOWED_NODES}")
    else:
        print(f"Gagal terhubung ke MQTT, code: {reason_code}")


def on_subscribe(client, userdata, mid, reason_codes, properties):
    # Cek apakah subscription berhasil (reason code < 128 berarti sukses)
    success_count = sum(1 for rc in reason_codes if rc < 128)
    failed_count = len(reason_codes) - success_count

    print(f"Subscribe result - Success: {success_count}, Failed: {failed_count}")
    if failed_count > 0:
        print(f"Failed reason codes: {[rc for rc in reason_codes if rc >= 128]}")


def on_message(client, userdata, msg):
    # DIAGNOSTIK 2: Cetak pesan mentah SEGERA setelah diterima
    print(f"--> Pesan mentah diterima di topik '{msg.topic}': {msg.payload.decode()}")

    try:
        # Extract node_id dari topik (format: base/topic/node_id)
        topic_parts = msg.topic.split("/")
        node_id_from_topic = topic_parts[-1] if len(topic_parts) > 0 else "unknown"

        # Filter: Hanya terima data dari node yang diizinkan
        if node_id_from_topic not in ALLOWED_NODES:
            print(f"Node {node_id_from_topic} tidak diizinkan. Data diabaikan.")
            return

        payload = json.loads(msg.payload.decode("utf-8"))

        # Ambil data dari payload
        node_id = payload.get("node_id", node_id_from_topic)

        # Double check: pastikan node_id di payload juga sesuai
        if node_id not in ALLOWED_NODES:
            print(f"Node ID dalam payload ({node_id}) tidak diizinkan. Data diabaikan.")
            return

        temp = payload.get("temperature")
        hum = payload.get("humidity")

        # Support both 'ts' and 'timestamp' field
        ts_val = payload.get("timestamp")
        if ts_val is None:
            ts_val = payload.get("ts")
        ts = float(ts_val) if ts_val is not None else datetime.now().timestamp()

        dt_object = datetime.fromtimestamp(ts)

        print(f"Data diterima dari {node_id}: T={temp}°C, H={hum}%")

        if temp is not None and hum is not None:
            cursor = db_conn.cursor()
            cursor.execute(
                "INSERT INTO climate (node_id, timestamp, temperature, humidity) VALUES (?, ?, ?, ?)",
                (node_id, dt_object.strftime("%Y-%m-%d %H:%M:%S"), temp, hum),
            )
            db_conn.commit()

            with data_lock:
                live_data.append((dt_object, temp, hum, node_id))  # Tambah node_id
        else:
            print(f"Data tidak lengkap dari {node_id}: temp={temp}, hum={hum}")

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

        # Get latest data for each node
        latest_data_per_node = {}
        for ts, temp, hum, node_id in live_data:
            if (
                node_id not in latest_data_per_node
                or ts > latest_data_per_node[node_id]["timestamp"]
            ):
                latest_data_per_node[node_id] = {
                    "timestamp": ts,
                    "temperature": temp,
                    "humidity": hum,
                }

    # --- Logika peringatan untuk SEMUA node ---
    alerts = []

    for node_id in ALLOWED_NODES:
        if node_id not in latest_data_per_node:
            # Node tidak mengirim data
            alerts.append(
                html.Div(
                    [
                        html.Span(
                            f"[{node_id}] ",
                            style={
                                "color": "#888",
                                "fontWeight": "bold",
                                "marginRight": "5px",
                            },
                        ),
                        html.Span(
                            "TIDAK ADA DATA",
                            style={"color": "#ff6666", "marginRight": "15px"},
                        ),
                    ]
                )
            )
            continue

        data = latest_data_per_node[node_id]
        temp = data["temperature"]
        hum = data["humidity"]
        ts = data["timestamp"]

        # Container untuk alert node ini
        node_alerts = [
            html.Span(
                f"[{node_id}] ",
                style={"color": "#888", "fontWeight": "bold", "marginRight": "5px"},
            )
        ]

        # Suhu alerts
        if temp < TEMP_LOW:
            node_alerts.append(
                html.Span(
                    f"Suhu RENDAH ({temp:.1f}°C)",
                    style={"color": "#33CFFF", "marginRight": "10px"},
                )
            )
        elif temp >= TEMP_VERY_HIGH:
            node_alerts.append(
                html.Span(
                    f"Suhu SANGAT TINGGI ({temp:.1f}°C)",
                    style={"color": "#ff3333", "marginRight": "10px"},
                )
            )
        elif temp > TEMP_HIGH:
            node_alerts.append(
                html.Span(
                    f"Suhu TINGGI ({temp:.1f}°C)",
                    style={"color": "#FF8800", "marginRight": "10px"},
                )
            )
        else:
            node_alerts.append(
                html.Span(
                    f"Suhu Normal ({temp:.1f}°C)",
                    style={"color": "#55dd55", "marginRight": "10px"},
                )
            )

        # Kelembaban alerts
        if hum < HUM_LOW:
            node_alerts.append(
                html.Span(
                    f"Kelembaban RENDAH ({hum:.1f}%)",
                    style={"color": "#ffa500", "marginRight": "10px"},
                )
            )
        elif hum > HUM_HIGH:
            node_alerts.append(
                html.Span(
                    f"Kelembaban TINGGI ({hum:.1f}%)",
                    style={"color": "#ffcc00", "marginRight": "10px"},
                )
            )
        else:
            node_alerts.append(
                html.Span(
                    f"Kelembaban Normal ({hum:.1f}%)",
                    style={"color": "#55ddaa", "marginRight": "10px"},
                )
            )

        # Timestamp
        node_alerts.append(
            html.Span(
                f"({ts.strftime('%H:%M:%S')})",
                style={"color": "#999", "fontSize": "0.9em"},
            )
        )

        # Tambahkan alert untuk node ini
        alerts.append(html.Div(children=node_alerts, style={"marginBottom": "8px"}))

    # Container untuk semua alerts
    alert_container = html.Div(children=alerts)

    # --- Grafik dengan color coding per node ---
    fig_suhu = go.Figure()
    fig_kelembaban = go.Figure()

    # Warna berbeda untuk setiap node
    node_colors = {
        "node_001": "#FF5733",
        "node_002": "#33FF57",
        "node_003": "#3357FF",
        "node_004": "#FF33F5",
    }

    for node_id in ALLOWED_NODES:
        # Filter data for this node
        node_timestamps = [ts for ts, _, _, nid in live_data if nid == node_id]
        node_temps = [temp for _, temp, _, nid in live_data if nid == node_id]
        node_hums = [hum for _, _, hum, nid in live_data if nid == node_id]

        if node_timestamps:  # Only add if there's data
            color = node_colors.get(node_id, "#FFFFFF")

            fig_suhu.add_trace(
                go.Scatter(
                    x=node_timestamps,
                    y=node_temps,
                    mode="lines+markers",
                    name=f"{node_id}",
                    line=dict(color=color, width=2),
                    marker=dict(size=6),
                )
            )

            fig_kelembaban.add_trace(
                go.Scatter(
                    x=node_timestamps,
                    y=node_hums,
                    mode="lines+markers",
                    name=f"{node_id}",
                    line=dict(color=color, width=2),
                    marker=dict(size=6),
                )
            )

    # Update layout untuk grafik suhu
    fig_suhu.update_layout(
        title="Grafik Suhu Real-time (Multi-Node)",
        yaxis_title="Suhu (°C)",
        template="plotly_dark",
        margin=dict(l=40, r=40, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        showlegend=True,
    )

    # Update layout untuk grafik kelembaban
    fig_kelembaban.update_layout(
        title="Grafik Kelembaban Real-time (Multi-Node)",
        xaxis_title="Waktu",
        yaxis_title="Kelembaban (%)",
        template="plotly_dark",
        margin=dict(l=40, r=40, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        showlegend=True,
    )

    return alert_container, fig_suhu, fig_kelembaban


# --- JALANKAN SERVER DAN INISIALISASI MQTT ---
if __name__ == "__main__":
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, CLIENT_ID)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.on_subscribe = on_subscribe

    try:
        mqtt_client.connect(MQTT_BROKER, 1883)
    except Exception as e:
        print(f"Gagal terhubung ke broker MQTT: {e}")
        sys.exit(1)

    mqtt_client.loop_start()

    print("=== Line Dashboard Multi-Node ===")
    print(f"Allowed Nodes: {ALLOWED_NODES}")
    print(f"MQTT Topics: {[f'{MQTT_TOPIC_BASE}/{node}' for node in ALLOWED_NODES]}")
    print("Dashboard akan berjalan di http://127.0.0.1:8050")

    app.run(debug=True, use_reloader=False)
