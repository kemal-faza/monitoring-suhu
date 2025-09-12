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
MQTT_TOPIC = "0013/climate"
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
        self.title("Real-time Climate Monitor (Optimized)")
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

        self.btn_start = tk.Button(control_frame, text="Start Listening", command=self.start_mqtt)
        self.btn_start.pack(side=tk.LEFT, padx=5)
        self.btn_stop = tk.Button(control_frame, text="Stop Listening", command=self.stop_mqtt, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=5)
        
        plot_frame = tk.Frame(self)
        plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        fig = Figure(figsize=(5, 6), dpi=100)
        self.ax_temp = fig.add_subplot(2, 1, 1)
        self.ax_hum = fig.add_subplot(2, 1, 2)
        fig.tight_layout(pad=3.0)

        # OPTIMASI 1: Setup elemen statis sekali saja
        self.ax_temp.set_title("Suhu")
        self.ax_temp.set_ylabel("Suhu (°C)")
        self.ax_temp.grid(True)
        self.ax_hum.set_title("Kelembaban")
        self.ax_hum.set_ylabel("Kelembaban (%)")
        self.ax_hum.set_xlabel("Waktu")
        self.ax_hum.grid(True)
        self.ax_hum.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

        # OPTIMASI 2: Buat objek garis dengan data kosong, lalu simpan objeknya
        # Koma setelah self.line_temp adalah untuk unpack list berisi satu elemen
        self.line_temp, = self.ax_temp.plot([], [], 'r-', marker='o', markersize=3)
        self.line_hum, = self.ax_hum.plot([], [], 'b-', marker='o', markersize=3)

        self.canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # OPTIMASI 3: Menggunakan init_func dan blit=True untuk performa tinggi
        self.ani = animation.FuncAnimation(fig, self.update_plot, init_func=self.init_plot,
                                           interval=1000, blit=True)

    def init_plot(self):
        """Fungsi inisialisasi untuk blitting."""
        self.line_temp.set_data([], [])
        self.line_hum.set_data([], [])
        # Harus mengembalikan iterable dari artist yang akan dianimasikan
        return self.line_temp, self.line_hum

    def setup_database(self):
        # ... (Tidak ada perubahan di sini)
        self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS climate (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                temperature REAL NOT NULL,
                humidity REAL NOT NULL
            )""")
        self.conn.commit()
        print(f"Database '{DB_FILE}' siap.")

    def update_plot(self, frame):
        # ... (Logika pengambilan data dari queue tidak berubah)
        while not data_queue.empty():
            try:
                data = data_queue.get_nowait()
                temp = data.get("temperature")
                hum = data.get("humidity")
                ts = data.get("ts", datetime.now().timestamp())
                dt_object = datetime.fromtimestamp(ts)

                if temp is not None and hum is not None:
                    cursor = self.conn.cursor()
                    cursor.execute("INSERT INTO climate (timestamp, temperature, humidity) VALUES (?, ?, ?)",
                                   (dt_object.strftime("%Y-%m-%d %H:%M:%S"), temp, hum))
                    self.conn.commit()
                    # print(f"Data tersimpan: {dt_object} - Temp: {temp}°C, Hum: {hum}%") # Optional: matikan agar tidak spam terminal

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
            return self.line_temp, self.line_hum

        # OPTIMASI 4: Update data garis, jangan clear() dan plot() ulang
        self.line_temp.set_data(self.timestamps, self.temperatures)
        self.line_hum.set_data(self.timestamps, self.humidities)

        # OPTIMASI 5: Hitung ulang batas sumbu secara manual
        self.ax_temp.relim()
        self.ax_temp.autoscale_view()
        self.ax_hum.relim()
        self.ax_hum.autoscale_view()
        
        # Sinkronkan sumbu x jika perlu
        self.ax_hum.set_xlim(self.ax_temp.get_xlim())
        self.ax_hum.figure.autofmt_xdate()
        
        # Kembalikan artist yang telah diupdate agar blitting tahu apa yang harus digambar ulang
        return self.line_temp, self.line_hum

    def start_mqtt(self):
        # ... (Tidak ada perubahan di sini)
        if self.mqtt_thread is None or not self.mqtt_thread.is_alive():
            self.mqtt_thread = MqttThread(data_queue)
            self.mqtt_thread.start()
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
            print("Listener MQTT dimulai.")

    def stop_mqtt(self):
        # ... (Tidak ada perubahan di sini)
        if self.mqtt_thread and self.mqtt_thread.is_alive():
            self.mqtt_thread.stop()
            self.mqtt_thread.join()
            self.btn_start.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)
            print("Listener MQTT dihentikan.")

    def on_closing(self):
        # Hentikan animasi sebelum menutup untuk mencegah error
        if self.ani:
            self.ani.event_source.stop()
        if messagebox.askokcancel("Keluar", "Apakah Anda yakin ingin keluar?"):
            self.stop_mqtt()
            if self.conn:
                self.conn.close()
                print("Koneksi database ditutup.")
            self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()