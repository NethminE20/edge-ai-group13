#!/bin/bash
# Generate MQTT password file with valid hashes
# This script runs when mosquitto container starts

PASSWORD_FILE="/mosquitto/config/passwords.txt"

# Only generate if file doesn't exist or is empty
if [ ! -f "$PASSWORD_FILE" ] || [ ! -s "$PASSWORD_FILE" ]; then
    echo "Generating password file with valid hashes..."
    
    # Create empty password file
    > "$PASSWORD_FILE"
    
    # Add credentials using mosquitto_passwd (creates valid PBKDF2-SHA512 hashes)
    mosquitto_passwd -b "$PASSWORD_FILE" "edge-ai" "edge123"
    mosquitto_passwd -b "$PASSWORD_FILE" "dashboard" "dash123"
    mosquitto_passwd -b "$PASSWORD_FILE" "simulator" "sim123"
    
    echo "✓ Password file generated successfully"
    chmod 600 "$PASSWORD_FILE"
else
    echo "✓ Password file already exists"
fi
