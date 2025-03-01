#FROM ubuntu:latest
FROM python:3.9

WORKDIR /App

# Install necessary packages
RUN apt-get update && apt-get install -y cron

# Copy the cron file into the container
COPY mycron /etc/cron.d/mycron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/mycron

# Apply the cron job to the root user's crontab
RUN crontab /etc/cron.d/mycron

# Create a directory for notification logs
RUN mkdir -p /var/log

# Initialize the file
RUN echo "Initialized notification log file" > /var/log/notify.log

# Start the cron service in the foreground
CMD ["cron", "-f"]
