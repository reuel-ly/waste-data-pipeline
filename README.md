# Waste IoT Data Pipeline

A real-time data pipeline that ingests IoT sensor data from ESP32 microcontrollers, streams it through Apache Kafka via MQTT, processes it with PySpark Structured Streaming, and stores it in MongoDB Atlas.

---

## Architecture

```
ESP32 Sensors → MQTT (Mosquitto) → Kafka → PySpark Streaming → MongoDB Atlas
                                                ↑
                               OpenWeatherMap API (optional testing)
```

| Layer | Tool | Role |
|---|---|---|
| Edge Device | ESP32 | Collects and publishes sensor data via MQTT |
| MQTT Broker | Eclipse Mosquitto | Receives sensor data from ESP32 |
| Ingestion | Apache Kafka | Message broker for real-time data streaming |
| Processing | PySpark Structured Streaming | Cleans and transforms incoming data |
| Storage | MongoDB Atlas | Stores processed sensor readings |

---

## Tech Stack

- **ESP32** — IoT microcontroller for sensor data collection
- **Eclipse Mosquitto 2.0.22** — lightweight MQTT broker for IoT communication
- **Apache Kafka + Zookeeper** — real-time message streaming
- **Apache Spark (PySpark 4.1.1)** — structured streaming and data processing
- **MongoDB Atlas** — cloud database for processed data
- **Docker + Docker Compose** — containerized infrastructure
- **Python 3.10** — application code (conda environment on WSL2)
- **OpenWeatherMap API** — optional weather data source for testing

---

## Project Structure

```
waste-data-pipeline/
├── config/
│   ├── __init__.py
│   └── settings.py                  # centralized configuration
├── ingestion/
│   ├── __init__.py
│   ├── kafka_producer.py            # fetches OpenWeatherMap data (testing)
│   └── mqtt_to_kafka.py             # bridges MQTT messages to Kafka
├── processing/
│   ├── __init__.py
│   ├── spark_connector.py           # SparkSession setup (weather)
│   ├── spark_connector_iot.py       # SparkSession setup (IoT sensors)
│   ├── spark_streaming_job.py       # weather streaming pipeline
│   └── spark_streaming_job_iot.py   # IoT sensor streaming pipeline
├── storage/
│   ├── __init__.py
│   └── mongodb_connector.py         # MongoDB connection helpers
├── mosquitto/
│   └── config/
│       └── mosquitto.conf           # Mosquitto broker configuration
├── .env                             # environment variables (not committed)
├── .gitignore
├── docker-compose.yml               # infrastructure services
├── requirements.txt
├── setup.py
└── README.md
```

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) with WSL2 integration enabled
- [WSL2 (Ubuntu)](https://learn.microsoft.com/en-us/windows/wsl/install)
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) installed inside WSL2
- [MongoDB Atlas account](https://www.mongodb.com/atlas)
- [OpenWeatherMap API key](https://openweathermap.org/api) (optional)
- Java 17 installed inside WSL2 (`sudo apt install openjdk-17-jdk`)
- Arduino IDE with ESP32 board support and PubSubClient + ArduinoJson libraries

---

## Procedures

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/waste-data-pipeline.git
cd waste-data-pipeline
```

### 2. Create Conda Environment (inside WSL2)
```bash
conda create -n waste-pipeline python=3.10
conda activate waste-pipeline
pip install -e .
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the project root:
```bash
# OpenWeatherMap (optional — for testing)
OPENWEATHER_KEY=your_api_key_here
OPENWEATHER_URL=https://api.openweathermap.org/data/2.5/weather

# MongoDB Atlas
DATABASE_URL=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/

# Kafka
KAFKA_BROKER=localhost:29092
KAFKA_TOPIC=weather

# Spark
SPARK_APP_NAME=WasteDataPipeline
```

### 4. Start Docker Services
```bash
docker-compose up -d

# Verify all services are running
docker-compose ps
```

### 5. Set Up Windows Port Forwarding for ESP32 (Run in PowerShell as Admin)
```powershell
# Forward port 1883 from Windows WiFi to WSL
$wslIp = (wsl hostname -I).Trim()
netsh interface portproxy add v4tov4 `
  listenport=1883 `
  listenaddress=0.0.0.0 `
  connectport=1883 `
  connectaddress=$wslIp

# Allow port 1883 through Windows Firewall
New-NetFirewallRule -DisplayName "MQTT 1883" `
  -Direction Inbound -Protocol TCP `
  -LocalPort 1883 -Action Allow
```

> WSL2 IP changes on every restart. Please re-run this command if ESP32 can't connect after restarting your PC.

### 6. Flash ESP32

Create `secrets.h` in your Arduino sketch folder:
```cpp
#define WIFI_SSID     "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"
#define MQTT_BROKER   "YOUR_PC_WIFI_IP"   // run ipconfig to find this
#define MQTT_PORT     1883
```

Upload the sketch via Arduino IDE. Always disconnect sensor wires during upload to avoid flash corruption.

---

## Running the IoT Pipeline

**Terminal 1 — MQTT to Kafka Bridge:**
```bash
conda activate waste-pipeline
python -m ingestion.mqtt_to_kafka
```

**Terminal 2 — IoT PySpark Streaming Job:**
```bash
conda activate waste-pipeline
python -m processing.spark_streaming_job_iot
```

**Terminal 3 — Connect ESP32 via USB**
- Open Arduino IDE Serial Monitor at `115200` baud
- ESP32 automatically connects to WiFi and starts publishing sensor data

---

## Running the Weather Pipeline (Optional Testing)

**Terminal 1 — Kafka Producer:**
```bash
conda activate waste-pipeline
python -m ingestion.kafka_producer
```

**Terminal 2 — Weather PySpark Streaming Job:**
```bash
conda activate waste-pipeline
python -m processing.spark_streaming_job
```

---

## Docker Services

| Service | Port | Description |
|---|---|---|
| Kafka | 9092 / 29092 | Message broker |
| Zookeeper | 2181 | Kafka dependency |
| Spark Master | 8080 / 7077 | Spark cluster manager |
| Spark Worker | — | Spark compute node |
| MongoDB | 27017 | Local MongoDB (dev only) |
| Mosquitto | 1883 / 9001 | MQTT broker for ESP32 |

Access the **Spark UI** at `http://localhost:8080`

---

## IoT Data Schema

Each sensor reading stored in MongoDB (`iot_db.sensor_readings`):

```json
{
    "sensor_id":   "ESP32_001",
    "location":    "Zone A - Bin 1",
    "waste_level": 67.3,
    "distance_cm": 12.4,
    "battery":     85,
    "unit":        "%",
    "simulated":   true,
    "ingested_at": "2026-03-14T17:50:00"
}
```

---

## Useful Commands

```bash
# Start all services
docker-compose up -d

# Stop all services (data preserved)
docker-compose down

# View service logs
docker-compose logs -f kafka
docker-compose logs -f mosquitto

# Check IoT Kafka topic messages
docker exec -it kafka bash
kafka-console-consumer --topic iot-sensors --bootstrap-server localhost:9092 --from-beginning

# Clear Spark checkpoints
rm -rf /tmp/checkpoints/iot
rm -rf /tmp/checkpoints/mongo
```

---

## Requirements

```
pyspark==4.1.1
pymongo[srv]
kafka-python
paho-mqtt
python-dotenv
requests
```

---

## Notes
- MongoDB Atlas free tier supports up to **512MB** of storage
- WSL2 IP changes on every restart — re-run the port forwarding PowerShell command if ESP32 can't connect
- Always use `docker-compose down` (not `-v`) to preserve MongoDB data between sessions
- Always disconnect sensor wires before uploading code to ESP32 to avoid flash corruption