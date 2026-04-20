# edge-ai-group13
# 🔥 Fire Monitoring System (Edge AI)

This project is an Industrial IoT system using:

- MQTT (Mosquitto)
- Node-RED Dashboard
- Python Edge AI (ML anomaly detection)
- Docker (containerized setup)

---

## 🚀 Features

- Real-time gas monitoring
- ML-based anomaly detection
- Live dashboard (Gauge + Chart)
- Fire alert system
- Alarm trigger (UI)

---

## 🧱 Architecture

Python → MQTT → Node-RED → Dashboard

---

## 🐳 How to Run

### 1. Clone repo

### 2. Start system
docker-compose up --build

### 3. Open dashboard
http://localhost:1880/ui

### Services
Service	    Port
Node-RED	1880
MQTT	    1883

### MQTT Topics
alerts/group01/fire/status

### Notes
Make sure Docker is installed
Dashboard nodes auto-install on first run

### Dashboard Preview
Gas Level Gauge
Gas Trend Chart
Status Indicator
Fire Alert System




