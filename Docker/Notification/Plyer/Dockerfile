# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install dependencies including dbus, dbus-x11 (which provides dbus-launch),
# libglib2.0-bin, and libnotify-bin
RUN apt-get update && apt-get install -y \
    dbus \
    dbus-x11 \
    libglib2.0-bin \
    libnotify-bin \
  && rm -rf /var/lib/apt/lists/*

# Generate machine-id for DBus if not exists
RUN mkdir -p /var/lib/dbus && dbus-uuidgen --ensure=/var/lib/dbus/machine-id

# Set the working directory
WORKDIR /app

# Copy the Python notification script into the container
COPY notify.py .

# Install Python dependency: plyer
RUN pip install plyer

# Make the script executable
RUN chmod +x notify.py

# Set the default command to run the notification script.
CMD ["./notify.py"]
