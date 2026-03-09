# Configuration settings for the Weather Data Pipeline
import os
from dotenv import load_dotenv
load_dotenv()
OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")
OPENWEATHER_URL = os.getenv("OPENWEATHER_URL")

# Kafka
KAFKA_BROKER = "localhost:29092"
KAFKA_TOPIC = "weather"

# Spark
SPARK_APP_NAME = "WeatherPipeline"

#MongoDB
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")