from pymongo import MongoClient
from config.settings import MONGO_URI, MONGO_DB
from utils.spark_session import get_spark_session

def save_to_mongo(df, collection_name, mode="overwrite"):
    spark = get_spark_session()
    df.write.format("mongodb") \
        .mode(mode) \
        .option("database", MONGO_DB) \
        .option("collection", collection_name) \
        .save()
    print(f"Saved {df.count()} records → {collection_name}")

def load_from_mongo(collection_name):
    spark = get_spark_session()
    df = spark.read.format("mongodb") \
        .option("database", MONGO_DB) \
        .option("collection", collection_name) \
        .load()
    print(f"Loaded {df.count()} records ← {collection_name}")
    return df

def collection_exists(collection_name):
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    exists = collection_name in db.list_collection_names()
    client.close()
    return exists

def drop_collection(collection_name):
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    db[collection_name].drop()
    print(f"Dropped collection: {collection_name}")
    client.close()
