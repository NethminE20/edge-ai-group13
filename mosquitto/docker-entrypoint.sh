#!/bin/sh
set -e
PASSWORD_FILE="/mosquitto/config/passwords.txt"
echo "[INFO] Initializing Mosquitto password file..."
mosquitto_passwd -b "$PASSWORD_FILE" "edge-ai" "edge123" 2>/dev/null || true
mosquitto_passwd -b "$PASSWORD_FILE" "dashboard" "dash123" 2>/dev/null || true
mosquitto_passwd -b "$PASSWORD_FILE" "simulator" "sim123" 2>/dev/null || true
chmod 600 "$PASSWORD_FILE"
echo "[INFO] ✓ Password file ready"
exec /usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf
