import tkinter as tk
from tkinter import messagebox
import paho.mqtt.client as mqtt
import sqlite3
import json
from datetime import datetime
import threading
import queue

# Import untuk plotting
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import matplotlib.dates as mdates

# --- KONFIGURASI ---
MQTT_BROKER = "broker.hivemq.com"
MQTT_TOPIC = "Informatika/IoT-E/Kelompok9/climate"
DB_FILE = "climate_data.db"
# --------------------

data_queue = queue.Queue()


class MqttThread(threading.Thread):
    def __init__(self, queue_param):
        super().__init__()
        self.queue = queue_param
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "gui_client")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.running = False

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("MQTT Terhubung!")
            client.subscribe(MQTT_TOPIC)
        else:
            print(f"Gagal terhubung ke MQTT, code {rc}")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            self.queue.put(payload)
        except Exception as e:
            print(f"Error memproses pesan: {e}")

    def run(self):
        self.running = True
        print("Mencoba menghubungkan MQTT...")
        self.client.connect(MQTT_BROKER, 1883)
        self.client.loop_start()
        while self.running:
            pass
        self.client.loop_stop()
        self.client.disconnect()
        print("MQTT Terputus.")

    def stop(self):
        self.running = False


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Real-time Climate Monitor")
        # Menambah tinggi jendela untuk mengakomodasi 2 grafik
        self.geometry("800x700")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.timestamps = []
        self.temperatures = []
        self.humidities = []

        self.mqtt_thread = None
        self.setup_database()
        self.setup_ui()

    def setup_ui(self):
        control_frame = tk.Frame(self)
        control_frame.pack(pady=10)

        self.btn_start = tk.Button(
            control_frame, text="Start Listening", command=self.start_mqtt
        )
        self.btn_start.pack(side=tk.LEFT, padx=5)

        self.btn_stop = tk.Button(
            control_frame,
            text="Stop Listening",
            command=self.stop_mqtt,
            state=tk.DISABLED,
        )
        self.btn_stop.pack(side=tk.LEFT, padx=5)

        plot_frame = tk.Frame(self)
        plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- PERUBAHAN UTAMA 1: SETUP SUBPLOT ---
        # Membuat Figure yang akan berisi 2 subplot
        fig = Figure(figsize=(5, 6), dpi=100)

        # Membuat 2 subplot (2 baris, 1 kolom).
        # ax_temp adalah plot ke-1 (atas)
        self.ax_temp = fig.add_subplot(2, 1, 1)
        # ax_hum adalah plot ke-2 (bawah)
        self.ax_hum = fig.add_subplot(2, 1, 2)

        # Memberi jarak antar plot agar judul dan label tidak tumpang tindih
        fig.tight_layout(pad=3.0)

        self.canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.ani = animation.FuncAnimation(
            fig, self.update_plot, interval=1000, blit=False
        )

    def setup_database(self):
        self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS climate (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                temperature REAL NOT NULL,
                humidity REAL NOT NULL
            )"""
        )
        self.conn.commit()
        print(f"Database '{DB_FILE}' siap.")

    def update_plot(self, frame):
        # Bagian pengambilan data dari queue tidak berubah
        while not data_queue.empty():
            try:
                data = data_queue.get_nowait()
                temp = data.get("temperature")
                hum = data.get("humidity")
                ts = data.get("ts", datetime.now().timestamp())
                dt_object = datetime.fromtimestamp(ts)

                if temp is not None and hum is not None:
                    cursor = self.conn.cursor()
                    cursor.execute(
                        "INSERT INTO climate (timestamp, temperature, humidity) VALUES (?, ?, ?)",
                        (dt_object.strftime("%Y-%m-%d %H:%M:%S"), temp, hum),
                    )
                    self.conn.commit()
                    print(f"Data tersimpan: {dt_object} - Temp: {temp}°C, Hum: {hum}%")

                    self.timestamps.append(dt_object)
                    self.temperatures.append(temp)
                    self.humidities.append(hum)

                    if len(self.timestamps) > 50:
                        self.timestamps.pop(0)
                        self.temperatures.pop(0)
                        self.humidities.pop(0)
            except queue.Empty:
                pass

        if not self.timestamps:
            return

        # --- PERUBAHAN UTAMA 2: PLOTTING TERPISAH ---
        # Bersihkan kedua area plot sebelum menggambar ulang
        self.ax_temp.clear()
        self.ax_hum.clear()

        # --- Plot 1: Grafik Suhu (Atas) ---
        self.ax_temp.plot(
            self.timestamps, self.temperatures, "r-", marker="o", markersize=3
        )
        self.ax_temp.set_title("Suhu")
        self.ax_temp.set_ylabel("Suhu (°C)")
        self.ax_temp.grid(True)
        # Sembunyikan label sumbu-x di grafik atas agar tidak redundan
        self.ax_temp.tick_params(axis="x", labelbottom=False)

        # --- Plot 2: Grafik Kelembaban (Bawah) ---
        self.ax_hum.plot(
            self.timestamps, self.humidities, "b-", marker="o", markersize=3
        )
        self.ax_hum.set_title("Kelembaban")
        self.ax_hum.set_ylabel("Kelembaban (%)")
        self.ax_hum.set_xlabel("Waktu")
        self.ax_hum.grid(True)

        # Atur format waktu di sumbu-x untuk grafik bawah
        self.ax_hum.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        self.ax_hum.figure.autofmt_xdate()

        # Pastikan layout rapi setelah update
        self.ax_hum.figure.tight_layout(pad=3.0)

    def start_mqtt(self):
        if self.mqtt_thread is None or not self.mqtt_thread.is_alive():
            self.mqtt_thread = MqttThread(data_queue)
            self.mqtt_thread.start()
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
            print("Listener MQTT dimulai.")

    def stop_mqtt(self):
        if self.mqtt_thread and self.mqtt_thread.is_alive():
            self.mqtt_thread.stop()
            self.mqtt_thread.join()
            self.btn_start.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)
            print("Listener MQTT dihentikan.")

    def on_closing(self):
        if messagebox.askokcancel("Keluar", "Apakah Anda yakin ingin keluar?"):
            self.stop_mqtt()
            if self.conn:
                self.conn.close()
                print("Koneksi database ditutup.")
            self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
