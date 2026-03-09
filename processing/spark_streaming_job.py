from processing.spark_connector import SparkConnector
from pyspark.sql.functions import col

def run():
    print(" Starting PySpark Streaming Job...")
    print(" Kafka → PySpark → MongoDB Atlas")
    print("Press Ctrl+C to stop\n")

    connector = SparkConnector()

    try:
        df = connector.read_from_kafka()

        df_clean = df.filter(
            col("city").isNotNull() &
            col("temperature").isNotNull() &
            col("humidity").isNotNull()
        )

        query = connector.write_stream_to_mongo(
            df=df_clean,
            collection="weather_readings",
            checkpoint_path="/tmp/checkpoints/mongo"
        )

        print("Streaming job running")
        print("Data flowing: Kafka → PySpark → MongoDB Atlas\n")

        query.awaitTermination()

    except KeyboardInterrupt:
        print("\n Streaming job stopped.")
    finally:
        connector.stop()

if __name__ == "__main__":
    run()