# Waste IoT Data Pipeline

A real-time data pipeline that ingests IoT sensors data, streams it through Apache Kafka, processes it with PySpark Structured Streaming, and stores it in MongoDB Atlas.

---

## 🏗️ Architecture

```
IoT sensors → Kafka → PySpark Streaming → MongoDB Atlas
```

| Layer | Tool | Role |
|---|---|---|
| Ingestion | Apache Kafka | Message broker for real-time weather stream |
| Processing | PySpark Structured Streaming | Cleans and transforms incoming data |
| Storage | MongoDB Atlas | Stores processed weather readings |

---

## 🛠️ Tech Stack

- **Apache Kafka** + Zookeeper — real-time message streaming
- **Apache Spark (PySpark 4.1.1)** — structured streaming and data processing
- **MongoDB Atlas** — cloud database for processed data
- **Docker** — containerized infrastructure
- **Python 3.10** — application code
- **OpenWeatherMap API** — live weather data source

---

## 📁 Project Structure

```
waste-data-pipeline/
├── config/
│   ├── __init__.py
│   └── settings.py            # centralized configuration
├── ingestion/
│   ├── __init__.py
│   └── kafka_producer.py      # fetches weather data and sends to Kafka
├── processing/
│   ├── __init__.py
│   ├── spark_connector.py     # SparkSession setup and read/write methods
│   └── spark_streaming_job.py # main streaming pipeline logic
├── .env                       # environment variables (not committed)
├── .gitignore
├── docker-compose.yml         # infrastructure services
├── requirements.txt
└── README.md
```

---

## ⚙️ Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [WSL2 (Ubuntu)](https://learn.microsoft.com/en-us/windows/wsl/install)
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- [MongoDB Atlas account](https://www.mongodb.com/atlas)
- [OpenWeatherMap API key](https://openweathermap.org/api)
- Java 17 (installed inside WSL)

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/waste-data-pipeline.git
cd waste-data-pipeline
```

### 2. Create Conda Environment
```bash
conda create -n waste-pipeline python=3.10
conda activate waste-pipeline
pip install -e .
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the project root:
```bash
# OPTIONAL: OpenWeatherMap (for testing)
OPENWEATHER_KEY=your_api_key_here
OPENWEATHER_URL=https://api.openweathermap.org/data/2.5/weather

# MongoDB Atlas
DATABASE_URL=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/weather_db

# Kafka
KAFKA_BROKER=localhost:29092
KAFKA_TOPIC=Topic_name

# Spark
SPARK_APP_NAME=DataPipeLine
```

### 4. Start Docker Services
```bash
docker-compose up -d

# Verify all services are running
docker-compose ps
```

### 5. Run the Pipeline

**Terminal 1 — Start Kafka Producer:**
```bash
conda activate waste-pipeline
python -m ingestion.kafka_producer
```

**Terminal 2 — Start PySpark Streaming Job:**
```bash
conda activate waste-pipeline
python -m processing.spark_streaming_job
```

---

## 🐳 Docker Services

| Service | Port | Description |
|---|---|---|
| Kafka | 9092 / 29092 | Message broker |
| Zookeeper | 2181 | Kafka dependency |
| Spark Master | 8080 / 7077 | Spark cluster manager |
| Spark Worker | — | Spark compute node |
| MongoDB | 27017 | Local MongoDB (dev only) |

Access the **Spark UI** at `http://localhost:8080`

---

## 🔧 Useful Commands

```bash
# Start all services
docker-compose up -d

# Stop all services (data preserved)
docker-compose down

# View service logs
docker-compose logs -f kafka

# Check Kafka topic messages
docker exec -it waste-data-pipeline-kafka-1 bash
kafka-console-consumer --topic weather --bootstrap-server localhost:9092 --from-beginning
```

---

## 📦 Requirements

```
pyspark==4.1.1
pymongo[srv]
kafka-python
python-dotenv
requests
```

---

## ⚠️ Notes

- The `.env` file is excluded from version control — never commit API keys or credentials
- MongoDB Atlas free tier supports up to **512MB** of storage
- OpenWeatherMap free tier supports up to **1,000,000 API calls/month**
- Always use `docker-compose down` (not `-v`) to preserve MongoDB data between sessions
