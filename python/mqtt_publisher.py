import time
import json
import random
import pandas as pd
import paho.mqtt.client as mqtt

broker = "mqtt"
port = 1883
topic = "sensors/group01/fire/data"

client = mqtt.Client()

# Retry connection
while True:
    try:
        client.connect(broker, port)
        break
    except:
        print("Waiting for MQTT...")
        time.sleep(2)

# Load dataset (must be inside python folder)
df = pd.read_csv("AirQuality.csv")

# Clean dataset
df = df[['CO(GT)']].dropna()

while True:
    for _, row in df.iterrows():
        gas = float(row['CO(GT)'])

        # Inject anomaly (5% chance)
        if random.random() < 0.05:
            gas += random.uniform(5, 10)

        payload = {
            "gas": round(gas, 2),
            "timestamp": time.time()
        }

        client.publish(topic, json.dumps(payload))
        print("Published:", payload)

        time.sleep(1)