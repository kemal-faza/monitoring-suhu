import paho.mqtt.client as mqtt
import sqlite3
import json
from datetime import datetime

# --- KONFIGURASI ---
MQTT_BROKER = "broker.hivemq.com"  # Gunakan "localhost" jika skrip ini berjalan di mesin yang sama dengan Mosquitto
MQTT_TOPIC = "0013/climate"
DB_FILE = "climate_data.db"
# --------------------


def setup_database():
    """Membuat tabel di database jika belum ada."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS climate (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()
    print(f"Database '{DB_FILE}' siap.")


def on_connect(client, userdata, flags, rc):
    """Callback saat berhasil terhubung ke broker."""
    if rc == 0:
        print("Berhasil terhubung ke Broker MQTT!")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribe ke topic: {MQTT_TOPIC}")
    else:
        print(f"Gagal terhubung, return code {rc}\n")


def on_message(client, userdata, msg):
    """Callback saat menerima pesan dari topic."""
    try:
        # Decode payload dari byte ke string, lalu parse JSON
        payload = json.loads(msg.payload.decode("utf-8"))
        temp = payload.get("temperature")
        hum = payload.get("humidity")

        if temp is not None and hum is not None:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Masukkan data ke tabel
            cursor.execute(
                "INSERT INTO climate (timestamp, temperature, humidity) VALUES (?, ?, ?)",
                (timestamp, temp, hum),
            )
            conn.commit()
            conn.close()
            print(f"Data tersimpan: {timestamp} - Temp: {temp}°C, Hum: {hum}%")

    except Exception as e:
        print(f"Error memproses pesan: {e}")


# Inisialisasi awal
setup_database()

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "sqlite_logger")
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, 1883)

# Jalankan loop selamanya untuk tetap mendengarkan pesan
client.loop_forever()
