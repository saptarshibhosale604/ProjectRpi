import time
import paho.mqtt.client as mqtt

print("rpi-publisher.py Initialized")

# broker = "localhost"
broker = "NodeMCUClient"
topic = "home/loads"

client = mqtt.Client()
client.connect(broker)

# Send a command to turn on load01, off load02, etc.
print("Publishing01")
client.publish(topic, "load01=1")
time.sleep(2)
print("Publishing02")
client.publish(topic, "load02=0")
time.sleep(2)
print("Publishing03")
client.publish(topic, "load03=1")
time.sleep(2)
print("Publishing04")
client.publish(topic, "load04=0")
time.sleep(2)
print("Publishing05")
client.publish(topic, "load05=1")

print("rpi-publisher.py End")
