import config
import db
from mqtt_client import create_mqtt_client
import time

def main():
    time.sleep(5)
    try:
        print("Initializing database...")
        db.init_db()
        print("Database initialized successfully")
        client = create_mqtt_client()
        print("Connecting to MQTT broker...")
        client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
        print("Connected to MQTT broker, starting loop...")
        client.loop_forever()
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == "__main__":
    main()