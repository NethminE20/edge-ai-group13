import json
import time
import numpy as np
import paho.mqtt.client as mqtt
import joblib
import pandas as pd

# Load model + scaler
model = joblib.load("co_model.pkl")
scaler = joblib.load("scaler.pkl")

broker = "mqtt"
data_topic = "sensors/group01/fire/data"
alert_topic = "alerts/group01/fire/status"

client = mqtt.Client()

# Retry connection
while True:
    try:
        client.connect(broker, 1883)
        break
    except:
        print("Waiting for MQTT...")
        time.sleep(2)

def is_anomaly(value):
    value_df = pd.DataFrame([[value]], columns=["CO"])
    value_scaled = scaler.transform(value_df)
    prediction = model.predict(value_scaled)

    print(f"RAW: {value}, SCALED: {value_scaled}, PRED: {prediction}")

    return prediction[0] == -1

def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    gas = data["gas"]

    # Hybrid logic 
    if gas > 8:
        status = "🔥 FIRE (Threshold)"
    elif is_anomaly(gas):
        status = "⚠️ ANOMALY (ML)"
    else:
        status = "Normal"

    alert = {
        "gas": gas,
        "status": status
    }

    client.publish(alert_topic, json.dumps(alert))
    print("Processed:", alert)

client.subscribe(data_topic)
client.on_message = on_message
client.loop_forever()