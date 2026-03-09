import sys
import os
import json
import time
import requests
from datetime import datetime
from kafka import KafkaProducer
from config.settings import (
    KAFKA_BROKER,
    KAFKA_TOPIC,
    OPENWEATHER_KEY,
    OPENWEATHER_URL
)

# Connect to Kafka
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def fetch_weather(city):
    """Fetch current weather for a city from OpenWeatherMap."""
    params = {
        "q": city,
        "appid": OPENWEATHER_KEY,
        "units": "metric" 
    }

    response = requests.get(OPENWEATHER_URL, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ API Error for {city}: {response.status_code}")
        return None

"""Extract response.data into a structured format for Kafka."""
def parse_weather(data):
    return {
        "city": data.get("name", "N/A"),
        "country": data.get("sys", {}).get("country", "N/A"),
        "temperature": data.get("main", {}).get("temp", None),
        "feels_like": data.get("main", {}).get("feels_like", None),
        "temp_min": data.get("main", {}).get("temp_min", None),
        "temp_max": data.get("main", {}).get("temp_max", None),
        "humidity": data.get("main", {}).get("humidity", None),
        "pressure": data.get("main", {}).get("pressure", None),
        "weather_main": data.get("weather", [{}])[0].get("main", "N/A"),
        "weather_description": data.get("weather", [{}])[0].get("description", "N/A"),
        "wind_speed": data.get("wind", {}).get("speed", None),
        "wind_direction": data.get("wind", {}).get("deg", None),
        "cloudiness": data.get("clouds", {}).get("all", None),
        "visibility": data.get("visibility", None),
        "timestamp": datetime.now().isoformat()
    }

def run_producer():
    print("🌤️ OpenWeatherMap Producer started...")
    print(f"📍 Monitoring Manila, Philippines")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            print(f"📡 Fetching weather data for all cities...")
            raw_data = fetch_weather(city="Manila")

            if raw_data:
                parsed = parse_weather(raw_data)
                producer.send(KAFKA_TOPIC, value=parsed)
                print(f"✅ Sent → {parsed['city']}, {parsed['country']} | "
                        f"Temp: {parsed['temperature']}°C | "
                        f"{parsed['weather_description']}")

            print(f"\nWaiting 10 seconds before next fetch...\n")
            time.sleep(10)  # wait before next fetch

    except KeyboardInterrupt:
        print("\n⛔ Producer stopped.")
    finally:
        producer.close()
        print("Producer connection closed.")

if __name__ == "__main__":
    run_producer()