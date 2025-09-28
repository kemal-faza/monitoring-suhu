"""
Multi-Node Temperature Monitoring Dashboard - Line Chart
========================================================
Dashboard real-time untuk monitoring suhu multi-node dengan visualisasi diagram garis.
Menampilkan tren suhu dan kelembapan dari semua node dalam grafik time series.

Author: Kelompok 9 - Informatika IoT
"""

import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objs as go
import plotly.express as px
import paho.mqtt.client as mqtt
import sqlite3
import pandas as pd
import json
from datetime import datetime, timedelta
import threading
import time
from collections import deque, defaultdict
import numpy as np

# ================== KONFIGURASI ==================
# MQTT Configuration
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "Informatika/IoT-E/Kelompok9/multi_node/+"

# Database Configuration
DB_NAME = "multi_node_climate.db"

# Dashboard Configuration
MAX_DATA_POINTS = 50  # Maksimal data points yang ditampilkan
UPDATE_INTERVAL = 1000  # Interval update dashboard dalam ms
PORT = 8051  # Port untuk line chart dashboard (berbeda dari heatmap)

# ================== GLOBAL VARIABLES ==================
# Data storage untuk real-time plotting
node_data = defaultdict(lambda: {
    'timestamps': deque(maxlen=MAX_DATA_POINTS),
    'temperatures': deque(maxlen=MAX_DATA_POINTS),
    'humidity': deque(maxlen=MAX_DATA_POINTS),
    'last_update': None,
    'pos_x': 0,
    'pos_y': 0,
    'status': 'offline'
})

# MQTT Client
mqtt_client = None
mqtt_connected = False

# ================== DATABASE FUNCTIONS ==================
def init_database():
    """Initialize database dengan tabel yang diperlukan"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create climate_data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS climate_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id TEXT NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            pos_x REAL,
            pos_y REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create node_info table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS node_info (
            node_id TEXT PRIMARY KEY,
            name TEXT,
            location TEXT,
            pos_x REAL,
            pos_y REAL,
            last_seen DATETIME,
            status TEXT DEFAULT 'active'
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"📊 Database '{DB_NAME}' initialized successfully.")

def save_to_database(node_id, temperature, humidity, pos_x=0, pos_y=0):
    """Simpan data ke database"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Insert climate data
        cursor.execute('''
            INSERT INTO climate_data (node_id, temperature, humidity, pos_x, pos_y)
            VALUES (?, ?, ?, ?, ?)
        ''', (node_id, temperature, humidity, pos_x, pos_y))
        
        # Update node info
        cursor.execute('''
            INSERT OR REPLACE INTO node_info (node_id, pos_x, pos_y, last_seen, status)
            VALUES (?, ?, ?, datetime('now'), 'active')
        ''', (node_id, pos_x, pos_y))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

def get_historical_data(hours=1):
    """Ambil data historis dari database untuk inisialisasi grafik"""
    try:
        conn = sqlite3.connect(DB_NAME)
        query = '''
            SELECT node_id, temperature, humidity, pos_x, pos_y, timestamp
            FROM climate_data 
            WHERE timestamp >= datetime('now', '-{} hours')
            ORDER BY timestamp ASC
        '''.format(hours)
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        
    except Exception as e:
        print(f"❌ Error loading historical data: {e}")
    
    return pd.DataFrame()

# ================== MQTT FUNCTIONS ==================
def on_connect(client, userdata, flags, reason_code, properties):
    """Callback ketika MQTT terhubung"""
    global mqtt_connected
    if reason_code == 0:
        print("🔗 MQTT Connected! Subscribing to multi-node topics...")
        client.subscribe(MQTT_TOPIC)
        mqtt_connected = True
        print(f"📡 Listening to topic: {MQTT_TOPIC}")
    else:
        print(f"❌ MQTT Connection failed: {reason_code}")
        mqtt_connected = False

def on_message(client, userdata, msg):
    """Callback ketika menerima message MQTT"""
    try:
        # Parse topic untuk mendapatkan node_id
        topic_parts = msg.topic.split('/')
        if len(topic_parts) >= 5:
            node_id_from_topic = topic_parts[-1]
        else:
            print(f"⚠️ Invalid topic format: {msg.topic}")
            return
            
        # Parse payload JSON
        payload = json.loads(msg.payload.decode())
        
        # Validasi data
        required_fields = ['node_id', 'temperature', 'humidity']
        if not all(field in payload for field in required_fields):
            print(f"⚠️ Missing required fields in payload: {payload}")
            return
            
        node_id = payload['node_id']
        temperature = float(payload['temperature'])
        humidity = float(payload['humidity'])
        pos_x = float(payload.get('pos_x', 0))
        pos_y = float(payload.get('pos_y', 0))
        
        # Timestamp
        current_time = datetime.now()
        
        # Update global data storage
        node_data[node_id]['timestamps'].append(current_time)
        node_data[node_id]['temperatures'].append(temperature)
        node_data[node_id]['humidity'].append(humidity)
        node_data[node_id]['pos_x'] = pos_x
        node_data[node_id]['pos_y'] = pos_y
        node_data[node_id]['last_update'] = current_time
        node_data[node_id]['status'] = 'online'
        
        # Save to database
        save_to_database(node_id, temperature, humidity, pos_x, pos_y)
        
        print(f"📊 {node_id}: T={temperature}°C, H={humidity}%, Pos=({pos_x},{pos_y})")
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
    except Exception as e:
        print(f"❌ Message processing error: {e}")

def setup_mqtt():
    """Setup MQTT client"""
    global mqtt_client
    
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    
    try:
        print(f"🔄 Connecting to MQTT broker: {MQTT_BROKER}:{MQTT_PORT}")
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()
        return True
    except Exception as e:
        print(f"❌ MQTT connection error: {e}")
        return False

# ================== HELPER FUNCTIONS ==================
def check_node_status():
    """Check status node berdasarkan last update"""
    current_time = datetime.now()
    timeout_minutes = 2
    
    for node_id in node_data:
        if node_data[node_id]['last_update']:
            time_diff = current_time - node_data[node_id]['last_update']
            if time_diff > timedelta(minutes=timeout_minutes):
                node_data[node_id]['status'] = 'offline'
            else:
                node_data[node_id]['status'] = 'online'

def get_node_colors():
    """Generate warna unik untuk setiap node"""
    colors = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', 
        '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
        '#bcbd22', '#17becf'
    ]
    return colors

# ================== DASH APP ==================
# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Multi-Node Line Chart Dashboard"

# Define layout
app.layout = html.Div([
    html.Div([
        html.H1("🌡️ Multi-Node Temperature Monitoring", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '30px'}),
        
        html.Div([
            html.Div([
                html.H4("📊 Temperature Trends", style={'color': '#34495e'}),
                dcc.Graph(id='temperature-chart')
            ], className='chart-container', style={'width': '48%', 'display': 'inline-block'}),
            
            html.Div([
                html.H4("💧 Humidity Trends", style={'color': '#34495e'}),
                dcc.Graph(id='humidity-chart')
            ], className='chart-container', style={'width': '48%', 'float': 'right'})
        ]),
        
        html.Div([
            html.H4("📈 Combined Overview", style={'color': '#34495e', 'marginTop': '30px'}),
            dcc.Graph(id='combined-chart')
        ]),
        
        html.Div([
            html.H4("🔌 Node Status", style={'color': '#34495e', 'marginTop': '30px'}),
            html.Div(id='node-status')
        ]),
        
        # Auto-refresh component
        dcc.Interval(
            id='interval-component',
            interval=UPDATE_INTERVAL,
            n_intervals=0
        )
    ], style={'padding': '20px', 'fontFamily': 'Arial, sans-serif'})
])

# ================== DASH CALLBACKS ==================
@app.callback(
    [Output('temperature-chart', 'figure'),
     Output('humidity-chart', 'figure'),
     Output('combined-chart', 'figure'),
     Output('node-status', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    """Update semua chart dan status"""
    
    # Check node status
    check_node_status()
    
    colors = get_node_colors()
    
    # Temperature Chart
    temp_fig = go.Figure()
    
    # Humidity Chart  
    humid_fig = go.Figure()
    
    # Combined Chart
    combined_fig = go.Figure()
    
    # Node status cards
    status_cards = []
    
    color_idx = 0
    active_nodes = 0
    
    for node_id, data in node_data.items():
        if len(data['timestamps']) == 0:
            continue
            
        color = colors[color_idx % len(colors)]
        color_idx += 1
        
        # Prepare data
        times = list(data['timestamps'])
        temps = list(data['temperatures'])
        humids = list(data['humidity'])
        
        if len(times) == 0:
            continue
            
        # Temperature chart
        temp_fig.add_trace(go.Scatter(
            x=times,
            y=temps,
            mode='lines+markers',
            name=f'{node_id}',
            line=dict(color=color, width=2),
            marker=dict(size=6)
        ))
        
        # Humidity chart
        humid_fig.add_trace(go.Scatter(
            x=times,
            y=humids,
            mode='lines+markers',
            name=f'{node_id}',
            line=dict(color=color, width=2),
            marker=dict(size=6)
        ))
        
        # Combined chart - Temperature
        combined_fig.add_trace(go.Scatter(
            x=times,
            y=temps,
            mode='lines+markers',
            name=f'{node_id} - Temp',
            line=dict(color=color, width=2),
            marker=dict(size=4),
            yaxis='y'
        ))
        
        # Status card
        status = data['status']
        last_temp = temps[-1] if temps else 0
        last_humid = humids[-1] if humids else 0
        last_update = data['last_update'].strftime('%H:%M:%S') if data['last_update'] else 'Never'
        
        if status == 'online':
            active_nodes += 1
            
        status_color = '#27ae60' if status == 'online' else '#e74c3c'
        status_icon = '🟢' if status == 'online' else '🔴'
        
        status_cards.append(
            html.Div([
                html.H5(f'{status_icon} {node_id}', style={'margin': '5px', 'color': status_color}),
                html.P(f'T: {last_temp:.1f}°C | H: {last_humid:.1f}%', style={'margin': '5px'}),
                html.P(f'Pos: ({data["pos_x"]:.0f}, {data["pos_y"]:.0f})', style={'margin': '5px'}),
                html.P(f'Last: {last_update}', style={'margin': '5px', 'fontSize': '12px'})
            ], style={
                'border': f'1px solid {status_color}',
                'borderRadius': '10px',
                'padding': '10px',
                'margin': '10px',
                'width': '200px',
                'display': 'inline-block',
                'backgroundColor': '#f8f9fa'
            })
        )
    
    # Update chart layouts
    temp_fig.update_layout(
        title='Temperature Over Time',
        xaxis_title='Time',
        yaxis_title='Temperature (°C)',
        hovermode='x unified',
        showlegend=True
    )
    
    humid_fig.update_layout(
        title='Humidity Over Time',
        xaxis_title='Time', 
        yaxis_title='Humidity (%)',
        hovermode='x unified',
        showlegend=True
    )
    
    combined_fig.update_layout(
        title=f'Real-time Multi-Node Monitoring ({active_nodes} nodes active)',
        xaxis_title='Time',
        yaxis=dict(title='Temperature (°C)', side='left'),
        hovermode='x unified',
        showlegend=True,
        height=400
    )
    
    return temp_fig, humid_fig, combined_fig, status_cards

# ================== INITIALIZATION ==================
def load_historical_data():
    """Load historical data untuk inisialisasi"""
    print("📚 Loading historical data...")
    df = get_historical_data(hours=2)
    
    if not df.empty:
        for _, row in df.iterrows():
            node_id = row['node_id']
            
            node_data[node_id]['timestamps'].append(row['timestamp'])
            node_data[node_id]['temperatures'].append(row['temperature'])
            node_data[node_id]['humidity'].append(row['humidity'])
            node_data[node_id]['pos_x'] = row['pos_x']
            node_data[node_id]['pos_y'] = row['pos_y']
            node_data[node_id]['last_update'] = row['timestamp']
            node_data[node_id]['status'] = 'online'
        
        print(f"📊 Loaded data for {len(node_data)} nodes")
    else:
        print("📊 No historical data found")

# ================== MAIN ==================
if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Multi-Node Line Chart Dashboard Starting...")
    print("=" * 60)
    
    # Initialize database
    init_database()
    
    # Load historical data
    load_historical_data()
    
    # Setup MQTT
    mqtt_success = setup_mqtt()
    
    if mqtt_success:
        print("✅ MQTT setup successful")
    else:
        print("⚠️ MQTT setup failed, running in offline mode")
    
    print(f"🌐 Dashboard will be available at: http://127.0.0.1:{PORT}")
    print("📊 Features:")
    print("   - Real-time temperature & humidity line charts")
    print("   - Multi-node status monitoring")
    print("   - Historical data visualization")
    print("   - Auto-refresh every second")
    print("=" * 60)
    
    # Start dashboard
    try:
        app.run(debug=False, host='127.0.0.1', port=PORT)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
        if mqtt_client:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
        print("👋 Goodbye!")