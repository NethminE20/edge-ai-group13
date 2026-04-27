"""
Exhaust Fan Actuator Controller

Controls the exhaust fan based on:
1. Automatic mode: CO levels and anomaly detection
2. Manual mode: Dashboard commands
"""

import json
import time
import logging
import paho.mqtt.client as mqtt

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - ACTUATOR - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FanController:
    """Simulate exhaust fan control via MQTT"""
    
    def __init__(self, broker="mqtt", port=1883):
        self.broker = broker
        self.port = port
        self.fan_state = False  # OFF by default
        self.manual_mode = False
        self.manual_command = None
        self.lwt_topic = "system/fan-controller/status"
        
        self.client = mqtt.Client(client_id="fan-controller")
        
        # Set Last Will and Testament
        self.client.will_set(
            topic=self.lwt_topic,
            payload=json.dumps({"status": "OFFLINE", "timestamp": time.time()}),
            qos=1,
            retain=True
        )
        
        # Set username and password for authentication
        self.client.username_pw_set(username="edge-ai", password="edge123")
        
        # Retry connection with backoff
        max_retries = 10
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                self.client.connect(broker, port)
                logger.info(f"✓ Connected to MQTT broker at {broker}:{port} (authenticated as edge-ai)")
                # Publish online status
                self.client.publish(self.lwt_topic, json.dumps({"status": "ONLINE", "timestamp": time.time()}), qos=1, retain=True)
                break
            except Exception as e:
                retry_count += 1
                logger.warning(f"Connection attempt {retry_count}/{max_retries} failed: {e}")
                if retry_count >= max_retries:
                    logger.error("Max retries reached. Exiting...")
                    raise
                time.sleep(3)  # Wait 3 seconds before retry
        
        # Subscribe to fan control commands
        self.client.subscribe("commands/group01/fire/fan/control")
        self.client.on_message = self.on_command
        self.client.loop_start()
        
        logger.info("Fan controller initialized and listening for commands")
    
    def on_command(self, client, userdata, msg):
        """Handle fan control commands from Node-RED dashboard"""
        try:
            data = json.loads(msg.payload)
            command = data.get("command", "").upper()
            
            if command in ["ON", "OFF", "AUTO"]:
                self.manual_command = command
                if command == "AUTO":
                    self.manual_mode = False
                    logger.info("🌀 Fan set to AUTO mode")
                else:
                    self.manual_mode = True
                    if command == "ON":
                        self.fan_state = True
                        logger.info("🌀 Fan manually turned ON")
                    else:
                        self.fan_state = False
                        logger.info("🌀 Fan manually turned OFF")
                
                self.publish_state()
            else:
                logger.warning(f"Unknown command: {command}")
        except json.JSONDecodeError:
            logger.error("Failed to decode command JSON")
        except Exception as e:
            logger.error(f"Command processing error: {e}")
    
    def auto_control(self, gas_level, anomaly_detected):
        """Automatic fan control based on CO levels and anomalies"""
        if not self.manual_mode:  # Only auto-control if not in manual mode
            previous_state = self.fan_state
            
            # Fan ON if: CO > 8 ppm OR anomaly detected
            if gas_level > 8 or anomaly_detected:
                self.fan_state = True
            else:
                self.fan_state = False
            
            # Only log state changes
            if self.fan_state != previous_state:
                state_str = "ON" if self.fan_state else "OFF"
                logger.info(f"🌀 Fan AUTO control: {state_str} (Gas: {gas_level} ppm, Anomaly: {anomaly_detected})")
            
            self.publish_state()
    
    def publish_state(self):
        """Publish current fan state to MQTT"""
        try:
            payload = {
                "fan": "ON" if self.fan_state else "OFF",
                "mode": "MANUAL" if self.manual_mode else "AUTO",
                "timestamp": time.time()
            }
            
            self.client.publish(
                "actuators/group01/fire/fan/state",
                json.dumps(payload),
                qos=1
            )
            logger.debug(f"Published fan state: {payload['fan']} ({payload['mode']} mode)")
        except Exception as e:
            logger.error(f"Failed to publish fan state: {e}")
    
    def get_state(self):
        """Return current fan state"""
        return {
            "state": "ON" if self.fan_state else "OFF",
            "mode": "MANUAL" if self.manual_mode else "AUTO"
        }
    
    def stop(self):
        """Gracefully stop the fan controller"""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("Fan controller stopped")
        except Exception as e:
            logger.error(f"Error stopping fan controller: {e}")


# Global fan controller instance
fan_controller = None


def initialize_fan_controller(broker="mqtt", port=1883):
    """Initialize the global fan controller"""
    global fan_controller
    fan_controller = FanController(broker=broker, port=port)
    return fan_controller


def control_fan_auto(gas_level, anomaly_detected):
    """Auto-control fan based on sensor data"""
    if fan_controller:
        fan_controller.auto_control(gas_level, anomaly_detected)


def get_fan_state():
    """Get current fan state"""
    if fan_controller:
        return fan_controller.get_state()
    return {"state": "OFF", "mode": "AUTO"}


def stop_fan_controller():
    """Stop the fan controller"""
    global fan_controller
    if fan_controller:
        fan_controller.stop()
        fan_controller = None
