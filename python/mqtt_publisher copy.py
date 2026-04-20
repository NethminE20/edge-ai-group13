import time
import json
import random
import pandas as pd
import paho.mqtt.client as mqtt

broker = "mqtt"
port = 1883
topic = "sensors/group01/fire/data"

client = mqtt.Client()
client.connect(broker, port)

# Load dataset
df = pd.read_csv("AirQuality.csv", sep=';')

# Clean column names
df.columns = df.columns.str.strip()

# Convert CO(GT)
df["CO(GT)"] = df["CO(GT)"].astype(str).str.replace(",", ".")
df["CO(GT)"] = pd.to_numeric(df["CO(GT)"], errors='coerce')

# Remove invalid values
df = df[df["CO(GT)"] != -200]

# Keep only needed column
df = df[['CO(GT)']].dropna()

while True:
    for _, row in df.iterrows():
        gas = float(row["CO(GT)"])

        # Inject anomaly
        if random.random() < 0.05:
            gas += random.uniform(5, 10)

        payload = {
            "gas": round(gas, 2),
            "timestamp": time.time()
        }

        client.publish(topic, json.dumps(payload))
        print("Published:", payload)

        time.sleep(1)