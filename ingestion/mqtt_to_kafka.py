import json
import paho.mqtt.client as mqtt
from kafka import KafkaProducer
from config.settings import KAFKA_BROKER, KAFKA_TOPIC_IOT

# Kafka producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe("iot/sensors")  # subscribe to ESP32 topic
        print("Listening for ESP32 data on 'iot/sensors'...")
    else:
        print(f"Failed to connect, code: {rc}")

def on_message(client, userdata, msg):
    try:
        # Parse incoming MQTT message
        payload = json.loads(msg.payload.decode('utf-8'))
        print(f"Received from ESP32: {payload}")

        # Forward to Kafka
        producer.send(KAFKA_TOPIC_IOT, value=payload)
        print(f"Forwarded to Kafka: {payload['sensor_id']}")

    except Exception as e:
        print(f"Error processing message: {e}")

# MQTT client setup
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect("localhost", 1883)
mqtt_client.loop_forever()