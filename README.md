# 🔥 Edge AI Fire Monitoring System

An industrial IoT solution for real-time fire detection using machine learning anomaly detection, MQTT messaging, automated actuator control, and live dashboard visualization.

## ✨ Features

- **Real-time Gas Monitoring** - Live CO sensor readings with MQTT
- **ML Anomaly Detection** - Isolation Forest for anomaly classification
- **Hybrid Alert System** - Threshold-based + ML-driven detection
- **Automated Actuator Control** - Exhaust fan auto-control with manual override
- **Live Dashboard** - Real-time gauge, charts, and status indicators with fan controls
- **Fire Alerts** - Trigger alarms and notifications
- **🔐 MQTT Authentication** - Username/password + Access Control Lists (ACL)
- **🛡️ MQTT Last Will & Testament** - Automatic failure detection + auto-reconnection
- **Containerized Deployment** - Full Docker setup

## 🏗️ Architecture

```
Sensor Data (CSV) 
    ↓
MQTT Publisher (Python) 
    ↓
MQTT Broker (Mosquitto) 
    ├→ Edge AI Detector (Python + ML)
    │   ↓
    │   Automated Fan Control (Actuator)
    ↓
Node-RED Dashboard 
    ↓
Web UI (http://localhost:1880/ui)
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### Run with Docker (Recommended)
```bash
git clone <repository>
cd edge-ai-group13
docker-compose up --build
```

Access dashboard: **http://localhost:1880/ui**

### Local Development
See [SETUP.md](SETUP.md) for detailed local setup instructions.

## 📊 System Components

### 1. **MQTT Broker** (Port 1883)
- **Service**: Mosquitto 2.0
- **Purpose**: Message routing between services
- **Config**: `mosquitto/mosquitto.conf`

### 2. **Python Publisher** (`python/mqtt_publisher.py`)
- Loads historical CO data from `AirQuality.csv`
- Simulates real-time sensor readings
- Injects 5% anomalies for testing
- **Topic**: `sensors/group13/fire/data`

### 3. **ML Detector** (`python/edge_ai.py`)
- **Algorithm**: Isolation Forest (Scikit-learn)
- **Detects**: Anomalies in CO levels
- **Hybrid Logic**:
  - `gas > 8 ppm` → 🔥 FIRE (Threshold)
  - ML Anomaly → ⚠️ ANOMALY
  - Normal → ✓ Normal
- **Output Topic**: `alerts/group13/fire/status`
- **Automatic Control**: Triggers fan when threshold or anomaly detected

### 4. **Fan Actuator Controller** (`python/actuator_controller.py`) 🔴 NEW
- Simulates exhaust fan control
- **Auto Mode**: Fan turns ON when CO > 8 ppm or anomaly detected
- **Manual Mode**: Controlled via dashboard buttons
- Supports three commands: ON, OFF, AUTO
- **Command Topic**: `commands/group13/fire/fan/control`
- **State Topic**: `actuators/group13/fire/fan/state`

### 5. **Node-RED Dashboard** (Port 1880)
- Real-time CO level gauge and trend chart
- Status indicators (Normal/Anomaly/Fire)
- **Fan Control Panel**:
  - 🔄 ON button - Turn fan on
  - ⏹️ OFF button - Turn fan off
  - 🤖 AUTO button - Enable automatic control
  - Status display showing current mode
- Notification and alarm system

## 🔧 Configuration

### MQTT Topics & Data Flow

| Topic | Direction | Purpose | Format |
|-------|-----------|---------|--------|
| `sensors/group13/fire/data` | Pub → Broker | Raw sensor readings | `{"gas": 2.5, "timestamp": 1234567890}` |
| `alerts/group13/fire/status` | Detector → Dashboard | Alert notifications | `{"gas": 2.5, "status": "✓ Normal"}` |
| `commands/group13/fire/fan/control` | Dashboard → Fan | Fan control commands | `{"command": "ON"}` |
| `actuators/group13/fire/fan/state` | Fan → Dashboard | Fan state feedback | `{"fan": "ON", "mode": "MANUAL"}` |

### Service Ports

| Service | Port | URL |
|---------|------|-----|
| MQTT Broker | 1883 | `mqtt` (docker network) |
| Node-RED | 1880 | http://localhost:1880 |
| Dashboard | 1880/ui | http://localhost:1880/ui |

## 🌀 Fan Control System

### Operating Modes

**AUTO Mode (Default)**
- Fan activates when: CO > 8 ppm OR anomaly detected
- Fan deactivates when conditions normalize
- Automatic emergency response without manual intervention

**MANUAL Mode**
- User controls fan directly from dashboard
- Press ON/OFF buttons to control
- Overrides automatic logic while active
- Press AUTO to return to automatic mode

### Command Format
```json
{
  "command": "ON"      // or "OFF" or "AUTO"
}
```

### State Feedback
```json
{
  "fan": "ON",         // or "OFF"
  "mode": "AUTO",      // or "MANUAL"
  "timestamp": 1234567890
}
```

## 📁 Project Structure

```
edge-ai-group13/
├── docker-compose.yml          # Service orchestration
├── README.md                   # This file
├── SETUP.md                    # Local dev setup
├── CONTRIBUTING.md             # Contribution guidelines
│
├── mosquitto/
│   └── mosquitto.conf          # MQTT broker config
│
├── node-red/
│   ├── flows.json              # Dashboard + fan control config
│   ├── package.json            # Node-RED dependencies
│   └── settings.js             # Node-RED settings
│
├── python/
│   ├── main.py                 # Entry point (runs all processes)
│   ├── mqtt_publisher.py       # Sensor data publisher
│   ├── edge_ai.py              # ML anomaly detector
│   ├── actuator_controller.py  # Exhaust fan control
│   ├── test_model.py           # Model testing script
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile              # Python container image
│   ├── AirQuality.csv          # Historical CO data
│   ├── co_model.pkl            # Trained ML model
│   └── scaler.pkl              # Feature scaler
│
└── ML model/
    ├── Training Code.ipynb     # Model training notebook
    └── AirQuality.csv          # Training dataset
```

## 📊 Machine Learning Details

### Model: Isolation Forest
- **Training Data**: UCI Air Quality Dataset
- **Feature**: CO (Carbon Monoxide) levels
- **Contamination Rate**: 5%
- **Normalization**: StandardScaler
- **Files**: `co_model.pkl`, `scaler.pkl`

### Test Model
```bash
python python/test_model.py
```

## 🧪 Testing

### Unit Test
```bash
python python/test_model.py
```

### Integration Test with Docker
```bash
docker-compose up --build
# Monitor output for successful messages and fan responses
```

### Manual Test with Local MQTT
1. Start Mosquitto locally
2. Run publisher: `python python/mqtt_publisher.py`
3. Run detector: `python python/edge_ai.py`
4. Check messages: 
   ```bash
   mosquitto_sub -h localhost -t "alerts/group13/fire/status"
   mosquitto_sub -h localhost -t "actuators/group13/fire/fan/state"
   ```
5. Control fan:
   ```bash
   mosquitto_pub -h localhost -t "commands/group13/fire/fan/control" -m '{"command":"ON"}'
   ```

## 📚 Dependencies

**Python**:
- paho-mqtt - MQTT client
- pandas - Data processing
- numpy - Numerical computing
- scikit-learn - ML models
- matplotlib - Visualization
- joblib - Model serialization

**Node-RED**: Auto-installed from package.json

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Ideas for Enhancement
- Support multiple sensors and fans
- Email/SMS alerts
- Historical analytics and RUL estimation
- Advanced ML models (LSTM, ensemble methods)
- Web API for remote access
- Database integration (InfluxDB, PostgreSQL)
- Unit test coverage
- Sparkplug B topic format
- MQTT authentication

## 🛠️ Troubleshooting

### Ports Already in Use
```bash
docker-compose down
docker system prune
docker-compose up --build
```

### MQTT Connection Failed
- Ensure Mosquitto container is running: `docker ps`
- Check broker logs: `docker logs mqtt`

### Model Files Missing
Regenerate from training notebook:
```bash
jupyter notebook "ML model/Training Code.ipynb"
```

### No Data in Dashboard
1. Check publisher logs: `docker logs python-edge`
2. Check detector logs: `docker logs python-edge`
3. Verify MQTT subscription: `mosquitto_sub -h localhost -t "sensors/group13/fire/data"`

### Fan Not Responding
1. Check fan controller logs in edge_ai output
2. Verify command topic: `mosquitto_pub -h localhost -t "commands/group13/fire/fan/control" -m '{"command":"ON"}'`
3. Monitor fan state: `mosquitto_sub -h localhost -t "actuators/group13/fire/fan/state"`

## 👥 Authors

Group 13 - IoT & Edge AI Project

---

**Status**: Active Development  
**Last Updated**: 2026-04-27  
**Version**: 1.1.0 (with Fan Actuator Control)

### Dashboard Preview
Gas Level Gauge
Gas Trend Chart
Status Indicator
Fire Alert System




