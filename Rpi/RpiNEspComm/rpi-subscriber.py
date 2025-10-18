import paho.mqtt.client as mqtt

print("rpi-subscriber.py Initialized")

def on_message(client, userdata, message):
    print(f"Feedback received: {message.payload.decode()}")

client = mqtt.Client()
client.connect("localhost")
client.subscribe("home/loads/feedback")
client.on_message = on_message
client.loop_forever()

print("rpi-subscriber.py End")

