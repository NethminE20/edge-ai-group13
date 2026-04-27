import time
import json
import random
import pandas as pd
import paho.mqtt.client as mqtt

# ---------------- MQTT CONFIG ----------------
broker = "mqtt"
port = 1883

gas_topic = "factory/group01/fire/detector/data"
status_topic = "factory/group01/fire/detector/alert"

# ---------------- CONNECT MQTT ----------------
client = mqtt.Client()
client.connect(broker, port, 60)

# ---------------- LOAD DATASET ----------------
df = pd.read_csv("AirQuality.csv", sep=';')

# Clean column names
df.columns = df.columns.str.strip()

# Convert CO(GT) column
df["CO(GT)"] = df["CO(GT)"].astype(str).str.replace(",", ".")
df["CO(GT)"] = pd.to_numeric(df["CO(GT)"], errors='coerce')

# Remove invalid values
df = df[df["CO(GT)"] != -200]

# Keep only needed column
df = df[['CO(GT)']].dropna()

print("Dataset loaded. Starting publishing...\n")

# ---------------- MAIN LOOP ----------------
while True:
    for _, row in df.iterrows():
        gas = float(row["CO(GT)"])

        # Inject anomaly (simulate fire/spike)
        if random.random() < 0.05:
            gas += random.uniform(5, 10)

        gas = round(gas, 2)

        # ---------------- GAS PAYLOAD ----------------
        gas_payload = {
            "gas": gas,
            "timestamp": time.time()
        }

        client.publish(gas_topic, json.dumps(gas_payload))

        # ---------------- STATUS LOGIC ----------------
        if gas <= 10:
            status = "Normal"
        elif gas <= 15:
            status = "Warning"
        else:
            status = "Danger"

        status_payload = {
            "status": status,
            "timestamp": time.time()
        }

        client.publish(status_topic, json.dumps(status_payload))

        # ---------------- DEBUG OUTPUT ----------------
        print(f"Gas: {gas} ppm | Status: {status}")

        time.sleep(1)