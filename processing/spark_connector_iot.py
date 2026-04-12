from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, current_timestamp
from pyspark.sql.types import StructType, StringType, FloatType, BooleanType
from config.settings import (
    SPARK_APP_NAME_IOT,
    MONGO_URI,
    KAFKA_BROKER,
    KAFKA_TOPIC_IOT
)

class SparkConnector:
    def __init__(self):
        self.spark = self._create_session()
        self.schema = self._define_schema()

    def _create_session(self):
        return SparkSession.builder \
            .appName(f"{SPARK_APP_NAME_IOT}_IoT") \
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

    def _define_schema(self):
        """IoT ultrasonic sensor schema."""
        return StructType() \
            .add("sensor_id", StringType()) \
            .add("location", StringType()) \
            .add("distance_cm", FloatType()) \
            .add("waste_level", FloatType()) \
            .add("is_full", BooleanType()) \
            .add("unit", StringType())

    def read_from_kafka(self):
        raw_stream = self.spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", KAFKA_BROKER) \
            .option("subscribe", KAFKA_TOPIC_IOT) \
            .option("startingOffsets", "latest") \
            .load()

        parsed = raw_stream.select(
            from_json(col("value").cast("string"), self.schema).alias("data")
        ).select("data.*") \
         .withColumn("ingested_at", current_timestamp())

        return parsed

    def write_stream_to_mongo(self, df, collection, checkpoint_path="/tmp/checkpoints/iot"):
        return df.writeStream \
            .format("mongodb") \
            .option("spark.mongodb.write.connection.uri", MONGO_URI) \
            .option("spark.mongodb.write.database", "iot_db") \
            .option("spark.mongodb.write.collection", collection) \
            .outputMode("append") \
            .option("checkpointLocation", checkpoint_path) \
            .start()

    def stop(self):
        self.spark.stop()
        print("SparkSession stopped.")