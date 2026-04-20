import json
import time
import numpy as np
import pandas as pd
import paho.mqtt.client as mqtt
import joblib

# Load trained model
model = joblib.load("model.pkl")

# MQTT setup
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
    value = np.array([[value]])
    prediction = model.predict(value)
    return prediction[0] == -1  # -1 = anomaly

def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    gas = data["gas"]

    if gas > 8:
        status = "🔥 FIRE (Critical Threshold)"
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