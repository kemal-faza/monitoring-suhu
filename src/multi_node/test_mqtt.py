import paho.mqtt.client as mqtt
import json
import time

# Test script untuk debug MQTT connection
MQTT_BROKER = "broker.hivemq.com"
MQTT_TOPIC = "Informatika/IoT-E/Kelompok9/multi_node/+"

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    if reason_code == 0:
        print(f"Subscribing to: {MQTT_TOPIC}")
        result = client.subscribe(MQTT_TOPIC)
        print(f"Subscribe result: {result}")
    else:
        print(f"Failed to connect, return code {reason_code}")

def on_subscribe(client, userdata, mid, reason_codes, properties):
    print(f"Subscribed: {mid} {reason_codes}")

def on_message(client, userdata, msg):
    print(f"Message received!")
    print(f"Topic: {msg.topic}")
    print(f"Payload: {msg.payload.decode()}")
    try:
        data = json.loads(msg.payload.decode())
        print(f"Parsed JSON: {data}")
    except:
        print("Failed to parse JSON")
    print("-" * 50)

if __name__ == "__main__":
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "test_client")
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe 
    client.on_message = on_message

    print("Connecting to MQTT broker...")
    client.connect(MQTT_BROKER, 1883, 60)
    
    print("Listening for messages... Press Ctrl+C to stop")
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nDisconnecting...")
        client.disconnect()