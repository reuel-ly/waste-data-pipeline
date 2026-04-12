#!/bin/bash

echo "⛔ Stopping Waste IoT Data Pipeline..."

# Kill Python processes
pkill -f "mqtt_to_kafka"
pkill -f "spark_streaming_job_iot"
pkill -f "uvicorn"
pkill -f "streamlit"

# Stop Docker services
docker compose down

echo "✅ Pipeline stopped."