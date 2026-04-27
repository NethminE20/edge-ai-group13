import json
import time
import logging
import numpy as np
import paho.mqtt.client as mqtt
import joblib
import pandas as pd
from actuator_controller import initialize_fan_controller, control_fan_auto

# =========================
# LOGGING
# =========================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - DETECTOR - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =========================
# LOAD MODEL
# =========================
try:
    model = joblib.load("co_model.pkl")
    scaler = joblib.load("scaler.pkl")
    logger.info("ML model and scaler loaded successfully")
except FileNotFoundError as e:
    logger.error(f"Model files not found: {e}")
    exit(1)

# =========================
# CONFIG
# =========================
broker = "mqtt"
port = 1883

data_topic = "factory/group01/fire/detector/data"
alert_topic = "factory/group01/fire/detector/alert"
lwt_topic = "factory/group01/system/edge-ai/status"

USERNAME = "edge-ai"
PASSWORD = "1234"

# =========================
# MQTT CLIENT
# =========================
client = mqtt.Client(client_id="edge-ai-detector")

# 🔥 Last Will (OFFLINE)
client.will_set(
    topic=lwt_topic,
    payload=json.dumps({
        "status": "OFFLINE",
        "timestamp": time.time()
    }),
    qos=1,
    retain=True
)

# 🔐 Authentication
client.username_pw_set(USERNAME, PASSWORD)

# =========================
# RECONNECT HANDLING
# =========================
def on_disconnect(client, userdata, rc):
    logger.warning(f"Disconnected from MQTT (rc={rc})")

    while True:
        try:
            client.reconnect()
            logger.info("Reconnected to MQTT broker")

            # Publish ONLINE after reconnect
            client.publish(
                lwt_topic,
                json.dumps({
                    "status": "ONLINE",
                    "timestamp": time.time()
                }),
                qos=1,
                retain=True
            )
            break

        except Exception:
            logger.warning("Reconnect failed. Retrying in 3s...")
            time.sleep(3)

client.on_disconnect = on_disconnect

# =========================
# CONNECT WITH RETRY
# =========================
max_retries = 10
retry_count = 0

while retry_count < max_retries:
    try:
        client.connect(broker, port)
        logger.info(f"✓ Connected to MQTT broker at {broker}:{port} (authenticated)")

        # Publish ONLINE status
        client.publish(
            lwt_topic,
            json.dumps({
                "status": "ONLINE",
                "timestamp": time.time()
            }),
            qos=1,
            retain=True
        )

        break

    except Exception as e:
        retry_count += 1
        logger.warning(f"Connection attempt {retry_count}/{max_retries} failed: {e}")

        if retry_count >= max_retries:
            logger.error("Max retries reached. Exiting...")
            exit(1)

        time.sleep(3)

# =========================
# FAN CONTROLLER
# =========================
try:
    initialize_fan_controller(broker=broker, port=port)
    logger.info("Fan controller initialized")
except Exception as e:
    logger.error(f"Failed to initialize fan controller: {e}")

# =========================
# ANOMALY DETECTION
# =========================
def is_anomaly(value):
    try:
        value_df = pd.DataFrame([[value]], columns=["CO"])
        value_scaled = scaler.transform(value_df)
        prediction = model.predict(value_scaled)

        return prediction[0] == -1

    except Exception as e:
        logger.error(f"Anomaly detection error: {e}")
        return False

# =========================
# MESSAGE HANDLER
# =========================
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload)
        gas = data.get("gas")

        if gas is None:
            logger.warning("Invalid payload - missing gas value")
            return

        # Detection
        anomaly_detected = is_anomaly(gas)

        if gas > 8:
            status = "🔥 FIRE (Threshold)"
        elif anomaly_detected:
            status = "⚠️ ANOMALY (ML)"
        else:
            status = "✓ Normal"

        alert = {
            "gas": gas,
            "status": status
        }

        # Publish alert
        client.publish(alert_topic, json.dumps(alert), qos=1)

        logger.info(f"Gas: {gas} ppm | {status}")

        # Fan control
        control_fan_auto(gas, anomaly_detected)

    except json.JSONDecodeError:
        logger.error("Failed to decode JSON payload")

    except Exception as e:
        logger.error(f"Message processing error: {e}")

# =========================
# START LISTENING
# =========================
client.subscribe(data_topic)
client.on_message = on_message

logger.info(f"Listening on topic: {data_topic}")
logger.info("ML anomaly detector with fan control ready")

# =========================
# MAIN LOOP
# =========================
try:
    client.loop_forever()

except KeyboardInterrupt:
    logger.info("Detector shutting down...")

except Exception as e:
    logger.error(f"Runtime error: {e}")

finally:
    client.disconnect()
    logger.info("Detector stopped")