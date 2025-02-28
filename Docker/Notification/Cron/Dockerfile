# Use a lightweight Ubuntu base image
FROM ubuntu:latest

# Install necessary packages
RUN apt-get update && apt-get install -y \
    cron \
    tini \
    mailutils \
    && rm -rf /var/lib/apt/lists/*

# Copy the cron file into the container
COPY mycron /etc/cron.d/mycron
RUN chmod 0644 /etc/cron.d/mycron

# Copy the notification script
COPY notify.sh /notify.sh
RUN chmod +x /notify.sh

# Create a directory for notification logs
RUN mkdir -p /var/log

# Use tini as an init process and run crond in foreground mode with logging
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["cron", "-f", "-l", "2"]
