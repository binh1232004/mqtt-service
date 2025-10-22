import paho.mqtt.client as mqtt
import config
from db import save_message, update_sensor_status

# Callback when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully")
        client.subscribe(config.MQTT_TOPIC)
    else:
        print(f"Connection failed with code {rc}")

# Callback when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # print(f"Topic: {msg.topic}\nMessage: {msg.payload.decode()}")
    if(msg.topic.endswith("/cmd")):
        update_sensor_status(msg.topic.rsplit('/', 1)[0], msg.payload.decode().lower())
    else:
        save_message(msg.topic, msg.payload.decode())

def create_mqtt_client():
    client = mqtt.Client()
    if config.MQTT_USERNAME and config.MQTT_PASSWORD:
        client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    return client