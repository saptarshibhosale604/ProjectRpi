# Aim
- To establish communication between Rapsberry pi and Node MCU Esp8266 via MQTT Protocol

# CMDs

- Checking mqtt connection
mosquitto_sub -h 10.47.167.108 -t test/topic
mosquitto_pub -h 10.47.167.108 -t test/topic -m "Hello from client"
  
sudo nvim /etc/mosquitto/mosquitto.conf // config file for mosquitto

sudo systemctl restart mosquitto
