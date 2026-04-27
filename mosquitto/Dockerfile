FROM eclipse-mosquitto:2.0

# Copy the custom entrypoint
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

# Make it executable
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Set as entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
