from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, current_timestamp
from pyspark.sql.types import (
    StructType, StringType, FloatType, IntegerType
)
from config.settings import (
    SPARK_APP_NAME,
    MONGO_URI,
    KAFKA_BROKER,
    KAFKA_TOPIC
)

class SparkConnector:
    def __init__(self):
        self.spark = self._create_session()
        self.schema = self._define_schema()

    def _create_session(self):
        return SparkSession.builder \
            .appName(SPARK_APP_NAME) \
            .config("spark.mongodb.read.connection.uri", MONGO_URI) \
            .config("spark.mongodb.write.connection.uri", MONGO_URI) \
            .config(
                "spark.jars.packages",
                ",".join([
                    "org.apache.spark:spark-sql-kafka-0-10_2.13:4.1.0",
                    "org.mongodb.spark:mongo-spark-connector_2.13:10.3.0"
                ])
            ) \
            .config("spark.streaming.stopGracefullyOnShutdown", "true") \
            .getOrCreate()
            
    # TODO: Refactor the Schema for the Real IoT sensor data
    def _define_schema(self):
        return StructType() \
            .add("city", StringType()) \
            .add("country", StringType()) \
            .add("temperature", FloatType()) \
            .add("feels_like", FloatType()) \
            .add("temp_min", FloatType()) \
            .add("temp_max", FloatType()) \
            .add("humidity", IntegerType()) \
            .add("pressure", IntegerType()) \
            .add("weather_main", StringType()) \
            .add("weather_description", StringType()) \
            .add("wind_speed", FloatType()) \
            .add("wind_direction", IntegerType()) \
            .add("cloudiness", IntegerType()) \
            .add("visibility", IntegerType()) \
            .add("timestamp", StringType())

    def read_from_kafka(self):
        raw_stream = self.spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", KAFKA_BROKER) \
            .option("subscribe", KAFKA_TOPIC) \
            .option("startingOffsets", "latest") \
            .load()

        parsed = raw_stream.select(
            from_json(col("value").cast("string"), self.schema).alias("data")
        ).select("data.*") \
         .withColumn("ingested_at", current_timestamp())

        return parsed

    def write_stream_to_mongo(self, df, collection, checkpoint_path="/tmp/checkpoints/mongo"):
        return df.writeStream \
            .format("mongodb") \
            .option("spark.mongodb.write.connection.uri", MONGO_URI) \
            .option("spark.mongodb.write.database", "weather_db") \
            .option("spark.mongodb.write.collection", collection) \
            .outputMode("append") \
            .option("checkpointLocation", checkpoint_path) \
            .start()

    def read_from_mongo(self, collection):
        return self.spark.read \
            .format("mongodb") \
            .option("spark.mongodb.read.database", "weather_db") \
            .option("spark.mongodb.read.collection", collection) \
            .load()

    def stop(self):
        self.spark.stop()
        print("SparkSession stopped.")