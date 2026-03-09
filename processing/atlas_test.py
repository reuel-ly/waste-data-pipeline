# Run this quick test before spark_streaming_job.py
# save as test_atlas.py in project root

from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()

try:
    client = MongoClient(os.getenv("DATABASE_URL"))
    db = client["weather_db"]
    db.test.insert_one({"test": "Atlas connected!"})
    print("MongoDB Atlas connected successfully!")
    client.close()
except Exception as e:
    print(f"Connection failed: {e}")