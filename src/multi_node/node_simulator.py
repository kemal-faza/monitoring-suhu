import paho.mqtt.client as mqtt
import json
import time
import random
import threading
from datetime import datetime
import math

# --- KONFIGURASI ---
MQTT_BROKER = "broker.hivemq.com"
BASE_TOPIC = "Informatika/IoT-E/Kelompok9/multi_node"
FIELD_WIDTH = 100
FIELD_HEIGHT = 100

# Konfigurasi nodes yang akan disimulasikan
NODE_CONFIGS = [
    {
        "node_id": "sim_001",
        "pos_x": 25.0,
        "pos_y": 25.0,
        "base_temp": 28.0,
        "temp_variation": 3.0,
        "base_humidity": 65.0,
        "humidity_variation": 10.0,
        "update_interval": 2.0,  # detik
        "enabled": True
    },
    {
        "node_id": "sim_002", 
        "pos_x": 75.0,
        "pos_y": 25.0,
        "base_temp": 26.5,
        "temp_variation": 2.5,
        "base_humidity": 70.0,
        "humidity_variation": 8.0,
        "update_interval": 1.5,
        "enabled": True
    },
    {
        "node_id": "sim_003",
        "pos_x": 50.0,
        "pos_y": 75.0,
        "base_temp": 30.0,
        "temp_variation": 4.0,
        "base_humidity": 60.0,
        "humidity_variation": 12.0,
        "update_interval": 2.5,
        "enabled": True  # Set False untuk simulasi node mati
    }
]


class NodeSimulator:
    def __init__(self, config):
        self.config = config
        self.client = None
        self.running = False
        self.thread = None
        
    def connect_mqtt(self):
        """Setup MQTT client untuk node ini"""
        client_id = f"sim_{self.config['node_id']}_{random.randint(0, 1000)}"
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id)
        
        try:
            self.client.connect(MQTT_BROKER, 1883, 60)
            self.client.loop_start()
            print(f"✓ {self.config['node_id']} terhubung ke MQTT broker")
            return True
        except Exception as e:
            print(f"✗ {self.config['node_id']} gagal terhubung: {e}")
            return False
    
    def generate_sensor_data(self):
        """Generate data sensor yang realistis dengan variasi"""
        # Tambahkan variasi berdasarkan waktu (simulasi perubahan kondisi harian)
        time_factor = math.sin(time.time() / 3600) * 0.5  # Variasi lambat sepanjang jam
        
        # Temperature dengan noise dan trend
        temp_noise = random.uniform(-self.config['temp_variation'], self.config['temp_variation'])
        temperature = self.config['base_temp'] + temp_noise + (time_factor * 2)
        
        # Humidity dengan korelasi inverse terhadap temperature
        hum_noise = random.uniform(-self.config['humidity_variation'], self.config['humidity_variation'])
        humidity = self.config['base_humidity'] + hum_noise - (time_factor * 5)
        
        # Clamp values dalam range realistis
        temperature = max(15.0, min(45.0, temperature))
        humidity = max(20.0, min(95.0, humidity))
        
        return {
            "node_id": self.config['node_id'],
            "temperature": round(temperature, 2),
            "humidity": round(humidity, 2),
            "pos_x": self.config['pos_x'],
            "pos_y": self.config['pos_y'],
            "timestamp": datetime.now().timestamp()
        }
    
    def publish_data(self):
        """Publish data ke MQTT"""
        if not self.client:
            return False
            
        data = self.generate_sensor_data()
        topic = f"{BASE_TOPIC}/{self.config['node_id']}"
        
        try:
            payload = json.dumps(data)
            result = self.client.publish(topic, payload)
            
            if result.rc == 0:
                print(f"📡 {self.config['node_id']}: T={data['temperature']}°C, H={data['humidity']}% → {topic}")
                return True
            else:
                print(f"✗ {self.config['node_id']}: Gagal publish (rc={result.rc})")
                return False
                
        except Exception as e:
            print(f"✗ {self.config['node_id']}: Error publish - {e}")
            return False
    
    def run_simulation(self):
        """Main loop simulasi node"""
        print(f"🚀 Memulai simulasi {self.config['node_id']} di posisi ({self.config['pos_x']}, {self.config['pos_y']})")
        
        while self.running and self.config['enabled']:
            if self.publish_data():
                time.sleep(self.config['update_interval'])
            else:
                time.sleep(5)  # Retry delay jika gagal
        
        print(f"🛑 Simulasi {self.config['node_id']} berhenti")
    
    def start(self):
        """Start node simulator"""
        if not self.config['enabled']:
            print(f"⚠️  {self.config['node_id']} dinonaktifkan dalam konfigurasi")
            return False
            
        if self.connect_mqtt():
            self.running = True
            self.thread = threading.Thread(target=self.run_simulation, daemon=True)
            self.thread.start()
            return True
        return False
    
    def stop(self):
        """Stop node simulator"""
        self.running = False
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
        if self.thread:
            self.thread.join(timeout=2)


class MultiNodeSimulator:
    def __init__(self):
        self.simulators = []
        self.running = False
        
    def initialize_nodes(self):
        """Inisialisasi semua node simulator"""
        print("=== Multi-Node Temperature Field Simulator ===")
        print(f"MQTT Broker: {MQTT_BROKER}")
        print(f"Base Topic: {BASE_TOPIC}")
        print(f"Field Size: {FIELD_WIDTH}x{FIELD_HEIGHT}m")
        print()
        
        for config in NODE_CONFIGS:
            simulator = NodeSimulator(config)
            self.simulators.append(simulator)
            
            status = "ENABLED" if config['enabled'] else "DISABLED"
            print(f"Node {config['node_id']}: Pos({config['pos_x']}, {config['pos_y']}) - {status}")
        
        print()
    
    def start_simulation(self):
        """Start semua node simulators"""
        self.running = True
        active_nodes = 0
        
        for simulator in self.simulators:
            if simulator.start():
                active_nodes += 1
                time.sleep(0.5)  # Delay antar node startup
        
        print(f"✓ {active_nodes}/{len(self.simulators)} node aktif")
        
        if active_nodes == 0:
            print("❌ Tidak ada node aktif. Keluar...")
            return False
        
        return True
    
    def run_control_loop(self):
        """Loop kontrol utama dengan kemampuan dinamis disable node"""
        print("\n=== Kontrol Simulator ===")
        print("Tekan Enter untuk menu kontrol, atau Ctrl+C untuk keluar")
        
        try:
            while self.running:
                try:
                    # Non-blocking input check
                    import select
                    import sys
                    
                    if select.select([sys.stdin], [], [], 1) == ([sys.stdin], [], []):
                        input()  # Clear input
                        self.show_control_menu()
                except ImportError:
                    # Windows fallback - just wait
                    time.sleep(5)
                    
        except KeyboardInterrupt:
            print("\n🛑 Menghentikan simulasi...")
            self.stop_simulation()
    
    def show_control_menu(self):
        """Menu kontrol interaktif"""
        print("\n=== Menu Kontrol ===")
        for i, sim in enumerate(self.simulators):
            status = "RUNNING" if sim.running else "STOPPED"
            enabled = "ENABLED" if sim.config['enabled'] else "DISABLED"
            print(f"{i+1}. {sim.config['node_id']} - {status} ({enabled})")
        
        print(f"{len(self.simulators)+1}. Keluar")
        
        try:
            choice = int(input("Pilihan (1-{}): ".format(len(self.simulators)+1)))
            
            if choice == len(self.simulators)+1:
                self.running = False
            elif 1 <= choice <= len(self.simulators):
                sim = self.simulators[choice-1]
                if sim.running:
                    print(f"Menghentikan {sim.config['node_id']}...")
                    sim.stop()
                    sim.config['enabled'] = False
                else:
                    print(f"Memulai ulang {sim.config['node_id']}...")
                    sim.config['enabled'] = True
                    sim.start()
        except (ValueError, IndexError):
            print("Pilihan tidak valid!")
    
    def stop_simulation(self):
        """Stop semua simulators"""
        self.running = False
        for simulator in self.simulators:
            simulator.stop()
        print("✓ Semua node simulator dihentikan")


def simulate_node_failure():
    """Simulasi kegagalan node secara otomatis (opsional)"""
    # Bisa digunakan untuk testing otomatis kegagalan node
    pass


if __name__ == "__main__":
    simulator = MultiNodeSimulator()
    simulator.initialize_nodes()
    
    if simulator.start_simulation():
        print(f"\n📊 Dashboard dapat diakses di: http://127.0.0.1:8050")
        print("⚡ Data sedang dikirim ke dashboard...")
        
        try:
            # Simple control loop untuk Windows
            while simulator.running:
                print(f"\n📈 Simulasi berjalan... (Tekan Ctrl+C untuk berhenti)")
                time.sleep(10)
                
                # Status update setiap 10 detik
                active_count = sum(1 for sim in simulator.simulators if sim.running)
                print(f"Status: {active_count}/{len(simulator.simulators)} node aktif")
                
        except KeyboardInterrupt:
            print("\n🛑 Menghentikan simulasi...")
            simulator.stop_simulation()
    
    print("Simulasi selesai.")