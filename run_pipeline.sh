#!/bin/bash

# ══════════════════════════════════════════════
#   Waste IoT Data Pipeline - Startup Script
# ══════════════════════════════════════════════

echo "🚀 Starting Waste IoT Data Pipeline..."
echo "══════════════════════════════════════"

# ── Step 1: Start Docker Services ─────────────
echo "🐳 Starting Docker services..."
docker compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 15  # give Kafka and Mosquitto time to fully start

# ── Step 2: Verify Docker Services ────────────
echo "🔍 Checking services..."
docker compose ps

# ── Step 3: Create Kafka Topic ─────────────────
echo "📌 Creating Kafka topic..."
docker exec kafka kafka-topics \
  --create \
  --if-not-exists \
  --topic iot-sensors \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1

# ── Step 4: Activate Conda ────────────────────
echo "🐍 Activating conda environment..."
source ~/miniconda3/etc/profile.d/conda.sh
conda activate waste-pipeline

# ── Step 5: Start All Services in Background ──
echo "📡 Starting MQTT to Kafka bridge..."
python -m ingestion.mqtt_to_kafka &
MQTT_PID=$!

echo "🔥 Starting PySpark IoT Streaming Job..."
python -m processing.spark_streaming_job_iot &
SPARK_PID=$!

echo "🚀 Starting FastAPI..."
uvicorn api.main:app --host 0.0.0.0 --port 8000 &
FASTAPI_PID=$!

echo "🎨 Starting Streamlit Dashboard..."
streamlit run app.py &
STREAMLIT_PID=$!

# ── Step 6: Print Status ───────────────────────
echo ""
echo "══════════════════════════════════════"
echo "✅ Pipeline is running!"
echo "══════════════════════════════════════"
echo "📊 Streamlit Dashboard → http://localhost:8501"
echo "🚀 FastAPI Docs        → http://localhost:8000/docs"
echo "⚡ Spark UI            → http://localhost:8080"
echo "══════════════════════════════════════"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# ── Step 7: Wait and Handle Shutdown ──────────
trap "echo '⛔ Stopping pipeline...'; \
      kill $MQTT_PID $SPARK_PID $FASTAPI_PID $STREAMLIT_PID; \
      docker-compose down; \
      echo '✅ Pipeline stopped.'" SIGINT SIGTERM

# Keep script running
wait