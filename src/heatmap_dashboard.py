import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
import paho.mqtt.client as mqtt
import sqlite3
import json
import numpy as np
from datetime import datetime, timedelta
import threading
from collections import defaultdict
import sys
import random
import time

# --- KONFIGURASI ---
MQTT_BROKER = "broker.hivemq.com"
# Ganti topik wildcard dengan daftar node spesifik
ALLOWED_NODES = ["node_001", "node_002"]  # Tambahkan ini
MQTT_TOPIC_BASE = "Informatika/IoT-E/Kelompok9/multi_node"
DB_FILE = "multi_node_climate.db"
CLIENT_ID = f"multi_node_dashboard_{random.randint(0, 10000)}"

# --- KONFIGURASI FIELD MONITORING ---
FIELD_WIDTH = 100  # Lebar field dalam meter
FIELD_HEIGHT = 100  # Tinggi field dalam meter
NODE_RADIUS = 15  # Radius monitoring per node dalam meter
GRID_RESOLUTION = 5  # Resolusi grid untuk heatmap (meter per grid)

# --- THRESHOLD SUHU ---
TEMP_MIN = 15.0
TEMP_MAX = 40.0

# --- DATA STORAGE ---
node_data = defaultdict(dict)  # {node_id: {latest_data, last_seen, status}}
data_lock = threading.Lock()
NODE_TIMEOUT = 30  # Detik untuk menganggap node mati


def setup_database():
    """Setup database dengan tabel untuk multi-node monitoring"""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()

    # Tabel untuk data climate dari setiap node
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS multi_node_climate (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            pos_x REAL NOT NULL,
            pos_y REAL NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Tabel untuk informasi node (konfigurasi dan status)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS node_info (
            node_id TEXT PRIMARY KEY,
            pos_x REAL NOT NULL,
            pos_y REAL NOT NULL,
            radius REAL DEFAULT 15.0,
            status TEXT DEFAULT 'active',
            last_seen DATETIME,
            description TEXT
        )
    """
    )

    conn.commit()
    print(f"Database multi-node '{DB_FILE}' siap.")
    return conn


db_conn = setup_database()


def update_node_status():
    """Update status node berdasarkan last_seen"""
    with data_lock:
        current_time = datetime.now()
        for node_id, data in node_data.items():
            if "last_seen" in data:
                time_diff = (current_time - data["last_seen"]).total_seconds()
                if time_diff > NODE_TIMEOUT:
                    data["status"] = "offline"
                else:
                    data["status"] = "online"


# --- LOGIKA MQTT ---
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("MQTT Terhubung! Subscribe ke topik multi-node...")

        # Subscribe ke node spesifik saja
        for node_id in ALLOWED_NODES:
            topic = f"{MQTT_TOPIC_BASE}/{node_id}"
            result = client.subscribe(topic)
            print(f"Subscribe to {topic} - Result: {result}")

        print(f"Listening to nodes: {ALLOWED_NODES}")
    else:
        print(f"Gagal terhubung ke MQTT, code: {reason_code}")


def on_subscribe(client, userdata, mid, reason_codes, properties):
    print(f"Subscribe callback - MID: {mid}, Reason codes: {reason_codes}")


def on_message(client, userdata, msg):
    """
    Format pesan yang diharapkan:
    {
        "node_id": "node_001",
        "temperature": 25.6,
        "humidity": 60.2,
        "pos_x": 20.0,
        "pos_y": 30.0,
        "timestamp": 1695123456.789
    }
    """
    try:
        # Debug: print raw message
        print(
            f"Raw MQTT message - Topic: {msg.topic}, Payload: {msg.payload.decode('utf-8')}"
        )

        # Extract node_id dari topik (format: base/topic/node_id)
        topic_parts = msg.topic.split("/")
        node_id_from_topic = topic_parts[-1] if len(topic_parts) > 0 else "unknown"

        # Filter: Hanya terima data dari node yang diizinkan
        if node_id_from_topic not in ALLOWED_NODES:
            print(f"Node {node_id_from_topic} tidak diizinkan. Data diabaikan.")
            return

        print(f"Topic parts: {topic_parts}, Node ID from topic: {node_id_from_topic}")

        payload = json.loads(msg.payload.decode("utf-8"))

        # Ambil data dari payload
        node_id = payload.get("node_id", node_id_from_topic)

        # Double check: pastikan node_id di payload juga sesuai
        if node_id not in ALLOWED_NODES:
            print(f"Node ID dalam payload ({node_id}) tidak diizinkan. Data diabaikan.")
            return

        temp = payload.get("temperature")
        hum = payload.get("humidity")
        pos_x = payload.get("pos_x")
        pos_y = payload.get("pos_y")
        ts = payload.get("timestamp", datetime.now().timestamp())

        dt_object = datetime.fromtimestamp(ts)

        print(f"Data dari {node_id}: T={temp}°C, H={hum}%, Pos=({pos_x},{pos_y})")

        if all(v is not None for v in [temp, hum, pos_x, pos_y]):
            # Simpan ke database
            cursor = db_conn.cursor()
            cursor.execute(
                """
                INSERT INTO multi_node_climate 
                (node_id, timestamp, temperature, humidity, pos_x, pos_y) 
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    node_id,
                    dt_object.strftime("%Y-%m-%d %H:%M:%S"),
                    temp,
                    hum,
                    pos_x,
                    pos_y,
                ),
            )

            # Update atau insert node info
            cursor.execute(
                """
                INSERT OR REPLACE INTO node_info 
                (node_id, pos_x, pos_y, last_seen) 
                VALUES (?, ?, ?, ?)
            """,
                (node_id, pos_x, pos_y, dt_object.strftime("%Y-%m-%d %H:%M:%S")),
            )

            db_conn.commit()

            # Update data di memory
            with data_lock:
                node_data[node_id] = {
                    "temperature": temp,
                    "humidity": hum,
                    "pos_x": pos_x,
                    "pos_y": pos_y,
                    "timestamp": dt_object,
                    "last_seen": dt_object,
                    "status": "online",
                }

    except Exception as e:
        print(f"Error memproses pesan: {e}")


def generate_heatmap_data():
    """Generate data untuk heatmap berdasarkan posisi dan data node"""
    with data_lock:
        if not node_data:
            return None, None, None, None

    # Buat grid koordinat
    x_grid = np.arange(0, FIELD_WIDTH + GRID_RESOLUTION, GRID_RESOLUTION)
    y_grid = np.arange(0, FIELD_HEIGHT + GRID_RESOLUTION, GRID_RESOLUTION)
    X, Y = np.meshgrid(x_grid, y_grid)

    # Inisialisasi temperature grid
    temp_grid = np.full(X.shape, np.nan)

    # Untuk setiap titik di grid, hitung suhu berdasarkan node terdekat
    with data_lock:
        for i in range(len(y_grid)):
            for j in range(len(x_grid)):
                grid_x, grid_y = X[i, j], Y[i, j]

                # Cari node dalam radius dan hitung weighted average
                weights = []
                temps = []

                for node_id, data in node_data.items():
                    if "pos_x" not in data or "pos_y" not in data:
                        continue

                    node_x, node_y = data["pos_x"], data["pos_y"]
                    distance = np.sqrt((grid_x - node_x) ** 2 + (grid_y - node_y) ** 2)

                    # Hanya node dalam radius yang berkontribusi
                    if distance <= NODE_RADIUS:
                        # Weight berdasarkan inverse distance (node lebih dekat = weight lebih besar)
                        weight = 1.0 / (
                            distance + 0.1
                        )  # +0.1 untuk avoid division by zero
                        weights.append(weight)
                        temps.append(data["temperature"])

                # Hitung weighted average temperature
                if weights:
                    temp_grid[i, j] = np.average(temps, weights=weights)

    return X, Y, temp_grid, node_data.copy()


# --- APLIKASI DASH ---
app = dash.Dash(__name__)
app.title = "Multi-Node Temperature Monitoring"

app.layout = html.Div(
    style={
        "backgroundColor": "#1e1e1e",
        "color": "#FFFFFF",
        "fontFamily": "Arial, sans-serif",
        "padding": "20px",
        "minHeight": "100vh",
    },
    children=[
        html.Div(
            className="header",
            children=[
                html.H1(
                    "Multi-Node Temperature Field Monitoring",
                    style={"textAlign": "center", "marginBottom": "10px"},
                ),
                html.P(
                    "Visualisasi heatmap suhu dari multiple sensor nodes",
                    style={
                        "textAlign": "center",
                        "fontSize": "1.1em",
                        "color": "#cccccc",
                    },
                ),
            ],
        ),
        # Status nodes
        html.Div(
            id="nodes-status",
            style={
                "marginTop": "20px",
                "marginBottom": "20px",
                "padding": "15px",
                "backgroundColor": "#2a2a2a",
                "borderRadius": "8px",
                "border": "1px solid #444",
            },
        ),
        # Heatmap
        html.Div([dcc.Graph(id="heatmap-graph", style={"height": "600px"})]),
        # Controls
        html.Div(
            [
                html.Label("Update Interval (detik):", style={"marginRight": "10px"}),
                dcc.Slider(
                    id="update-interval-slider",
                    min=1,
                    max=10,
                    step=1,
                    value=2,
                    marks={i: str(i) for i in range(1, 11)},
                    tooltip={"placement": "bottom", "always_visible": True},
                ),
            ],
            style={"marginTop": "20px", "marginBottom": "20px"},
        ),
        # Auto-update component
        dcc.Interval(
            id="interval-component", interval=2000, n_intervals=0  # 2 seconds
        ),
    ],
)


@app.callback(
    [Output("nodes-status", "children"), Output("heatmap-graph", "figure")],
    [Input("interval-component", "n_intervals")],
)
def update_dashboard(_):
    # Update status node
    update_node_status()

    # Generate status nodes display
    with data_lock:
        nodes_status = []
        for node_id, data in node_data.items():
            status_color = "#00ff00" if data.get("status") == "online" else "#ff4444"
            last_temp = data.get("temperature", "N/A")
            last_hum = data.get("humidity", "N/A")
            pos_x = data.get("pos_x", "N/A")
            pos_y = data.get("pos_y", "N/A")

            nodes_status.append(
                html.Div(
                    [
                        html.Span(
                            f"● {node_id}",
                            style={
                                "color": status_color,
                                "fontWeight": "bold",
                                "marginRight": "15px",
                            },
                        ),
                        html.Span(f"T: {last_temp}°C", style={"marginRight": "10px"}),
                        html.Span(f"H: {last_hum}%", style={"marginRight": "10px"}),
                        html.Span(
                            f"Pos: ({pos_x}, {pos_y})", style={"marginRight": "10px"}
                        ),
                        html.Span(
                            f"Status: {data.get('status', 'unknown')}",
                            style={"color": "#cccccc"},
                        ),
                    ],
                    style={
                        "marginBottom": "8px",
                        "display": "inline-block",
                        "width": "100%",
                    },
                )
            )

    if not nodes_status:
        nodes_status = [
            html.Div("Menunggu data dari nodes...", style={"color": "#888888"})
        ]

    # Generate heatmap
    X, Y, temp_grid, nodes = generate_heatmap_data()

    if X is None:
        # Tampilan kosong jika belum ada data
        fig = go.Figure()
        fig.update_layout(
            title="Menunggu Data Node...", template="plotly_dark", height=600
        )
        return nodes_status, fig

    # Buat heatmap
    fig = go.Figure()

    # Tambahkan heatmap
    heatmap = go.Heatmap(
        x=X[0, :],
        y=Y[:, 0],
        z=temp_grid,
        colorscale="RdYlBu_r",  # Red-Yellow-Blue terbalik (merah = panas)
        zmin=TEMP_MIN,
        zmax=TEMP_MAX,
        colorbar=dict(title="Temperature (°C)"),
        hoverongaps=False,
        showscale=True,
    )
    fig.add_trace(heatmap)

    # Tambahkan posisi node sebagai scatter points
    node_x = []
    node_y = []
    node_text = []
    node_colors = []

    for node_id, data in nodes.items():
        if "pos_x" in data and "pos_y" in data:
            node_x.append(data["pos_x"])
            node_y.append(data["pos_y"])
            node_text.append(
                f"{node_id}<br>T: {data['temperature']}°C<br>H: {data['humidity']}%"
            )
            node_colors.append(
                "#00ff00" if data.get("status") == "online" else "#ff4444"
            )

    if node_x:
        fig.add_trace(
            go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers+text",
                marker=dict(
                    size=15,
                    color=node_colors,
                    symbol="circle",
                    line=dict(width=2, color="white"),
                ),
                text=[node_id for node_id in nodes.keys()],
                textposition="top center",
                textfont=dict(color="white", size=10),
                hovertext=node_text,
                hoverinfo="text",
                name="Sensor Nodes",
            )
        )

        # Tambahkan lingkaran radius untuk setiap node
        for i, (node_id, data) in enumerate(nodes.items()):
            if "pos_x" in data and "pos_y" in data:
                fig.add_shape(
                    type="circle",
                    xref="x",
                    yref="y",
                    x0=data["pos_x"] - NODE_RADIUS,
                    y0=data["pos_y"] - NODE_RADIUS,
                    x1=data["pos_x"] + NODE_RADIUS,
                    y1=data["pos_y"] + NODE_RADIUS,
                    line=dict(color=node_colors[i], width=2, dash="dash"),
                    fillcolor="rgba(0,0,0,0)",
                )

    fig.update_layout(
        title=f"Temperature Field Heatmap - {datetime.now().strftime('%H:%M:%S')}",
        xaxis_title="X Position (m)",
        yaxis_title="Y Position (m)",
        template="plotly_dark",
        height=600,
        xaxis=dict(range=[0, FIELD_WIDTH]),
        yaxis=dict(range=[0, FIELD_HEIGHT], scaleanchor="x", scaleratio=1),
        showlegend=False,
    )

    return nodes_status, fig


@app.callback(
    Output("interval-component", "interval"), [Input("update-interval-slider", "value")]
)
def update_interval(value):
    return value * 1000  # Convert to milliseconds


# --- MAIN ---
if __name__ == "__main__":
    # Setup MQTT
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, CLIENT_ID)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_subscribe = on_subscribe
    mqtt_client.on_message = on_message

    try:
        mqtt_client.connect(MQTT_BROKER, 1883, 60)
    except Exception as e:
        print(f"Gagal terhubung ke broker MQTT: {e}")
        sys.exit(1)

    mqtt_client.loop_start()

    print("=== Multi-Node Temperature Monitoring Dashboard ===")
    print(f"Database: {DB_FILE}")
    print(f"Allowed Nodes: {ALLOWED_NODES}")
    print(f"MQTT Topics: {[f'{MQTT_TOPIC_BASE}/{node}' for node in ALLOWED_NODES]}")
    print(f"Field Size: {FIELD_WIDTH}x{FIELD_HEIGHT}m")
    print(f"Node Radius: {NODE_RADIUS}m")
    print("Dashboard akan berjalan di http://127.0.0.1:8050")

    app.run(debug=True, use_reloader=False, port=8050)
