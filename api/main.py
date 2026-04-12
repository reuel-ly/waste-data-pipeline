from fastapi import FastAPI
from pymongo import MongoClient
from config.settings import MONGO_URI
from bson import ObjectId

def serialize(doc):
    doc["_id"] = str(doc["_id"])
    return doc

client = MongoClient(MONGO_URI)
db = client["iot_db"]
collection = db["sensor_readings"]
app = FastAPI(title="Waste IoT Pipeline API")


@app.get("/")
async def root():
    try:
        data = list(collection.find().limit(5))
        return {"message" : [serialize(doc) for doc in data]}
    except Exception as e:
        return {"error": str(e)}


@app.get("/readings")
def get_readings(limit: int = 10):
    readings = list(
        collection.find({}, {"_id": 0})
        .sort("ingested_at", -1)
        .limit(limit)
    )
    return {"data" : readings}

@app.get("/readings/{sensor_id}")
def get_readings_by_sensor(sensor_id: str, limit: int = 10):
    readings = list(
        collection.find({"sensor_id": sensor_id}, {"_id": 0})
        .sort("ingested_at", -1)
        .limit(limit)
    )
    return {"data": readings}

@app.get("/stats")
def get_stats():
    total = collection.count_documents({})
    avg = list(collection.aggregate([
        {"$group": {
            "_id": "$sensor_id",
            "avg_waste_level": {"$avg": "$waste_level"},
            "avg_battery": {"$avg": "$battery"},
            "total_readings": {"$sum": 1}
        }}
    ]))
    return {
        "total_readings": total,
        "per_sensor": avg
    }

@app.get("/latest")
def get_latest():
    latest = list(collection.aggregate([
        {"$sort": {"ingested_at": -1}},
        {"$group": {
            "_id": "$sensor_id",
            "latest": {"$first": "$$ROOT"}
        }}
    ]))

    for item in latest:
        item["latest"].pop("_id", None)
    return {"data": latest}

@app.get("/alerts")
def get_full_bins():
    """Return sensors where bin is currently full."""
    full_bins = list(collection.aggregate([
        {"$sort": {"ingested_at": -1}},
        {"$group": {
            "_id": "$sensor_id",
            "latest": {"$first": "$$ROOT"}
        }},
        {"$match": {"latest.is_full": True}}
    ]))
    for item in full_bins:
        item["latest"].pop("_id", None)
    return {"full_bins": full_bins, "count": len(full_bins)}

