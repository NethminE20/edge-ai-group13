"""
Edge AI Fire Monitoring System - Main Entry Point

This script runs the complete fire monitoring pipeline:
1. MQTT Publisher: Publishes simulated sensor data
2. Edge AI Detector: ML-based anomaly detection + automated fan control

Components:
- Sensor data acquisition (mqtt_publisher.py)
- ML-based anomaly detection (edge_ai.py)
- Automated exhaust fan control (via actuator_controller.py)
"""

import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - MAIN - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("🔥 Starting Edge AI Fire Monitoring System...")
logger.info("Components: Publisher, Detector, Fan Controller")

try:
    # Start Publisher process
    logger.info("Starting sensor data publisher...")
    p1 = subprocess.Popen(["python", "mqtt_publisher.py"])
    
    # Start Edge AI Detector process (includes fan controller)
    logger.info("Starting ML anomaly detector with fan control...")
    p2 = subprocess.Popen(["python", "edge_ai.py"])
    
    logger.info("All processes started. System ready!")
    logger.info("Open dashboard at: http://localhost:1880/ui")
    
    # Wait for completion
    p1.wait()
    p2.wait()
    
except KeyboardInterrupt:
    logger.info("Shutting down processes...")
    p1.terminate()
    p2.terminate()
    logger.info("Processes stopped")
except Exception as e:
    logger.error(f"Error: {e}")
    exit(1)