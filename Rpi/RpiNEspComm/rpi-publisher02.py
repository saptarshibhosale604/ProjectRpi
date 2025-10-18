import time
import paho.mqtt.client as mqtt

print("Initialized")
# broker = "10.47.167.108"  # Your MQTT broker IP
broker = "localhost"  # Your MQTT broker IP
topic = "home/load"

client = mqtt.Client()

client.connect(broker, 1883, 60)
client.loop_start()

for i in range(10):
    # Send load ON message
    client.publish(topic, "load=1")
    print("ON")
    time.sleep(2)
    # To turn off, send load=0
    client.publish(topic, "load=0")
    print("OFF")
    time.sleep(1)

client.loop_stop()
client.disconnect()

print("END")
