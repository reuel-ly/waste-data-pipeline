# Configuration settings for the Weather Data Pipeline
import os
from dotenv import load_dotenv
load_dotenv()
OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")
OPENWEATHER_URL = os.getenv("OPENWEATHER_URL")

# Kafka
KAFKA_BROKER = "localhost:29092"
KAFKA_TOPIC = "weather"
KAFKA_TOPIC_IOT = "iot-sensors"  # separate topic from weather

# Spark
SPARK_APP_NAME = "WeatherPipeline"
SPARK_APP_NAME_IOT = "WastePipeline"

#MongoDB
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

# MQTT
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "iot/sensors"

# FastAPI
API_URL = "http://127.0.0.1:8000/"