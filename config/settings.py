import os
from dotenv import load_dotenv

load_dotenv()

# Spark
SPARK_MASTER_URL = os.getenv("SPARK_MASTER_URL", "spark://localhost:7077")
SPARK_APP_NAME = os.getenv("SPARK_APP_NAME", "EarthquakeClustering")
SPARK_EXECUTOR_MEM = os.getenv("SPARK_EXECUTOR_MEM", "2g")
SPARK_DRIVER_MEM = os.getenv("SPARK_DRIVER_MEM", "2g")

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "earthquake_db")
MONGO_RAW_COL = os.getenv("MONGO_RAW_COLLECTION", "raw_earthquakes")
MONGO_CLEAN_COL = os.getenv("MONGO_CLEAN_COLLECTION", "clean_earthquakes")
MONGO_KMEANS_COL = os.getenv("MONGO_KMEANS_COLLECTION", "kmeans_results")
MONGO_BISECT_COL = os.getenv("MONGO_BISECT_COLLECTION", "bisecting_results")

# USGS API
USGS_BASE_URL = os.getenv("USGS_BASE_URL", "https://earthquake.usgs.gov/fdsnws/event/1/query")
USGS_FORMAT = os.getenv("USGS_FORMAT", "csv")
DATA_YEAR = int(os.getenv("DATA_YEAR", "2025"))
MONTHS = list(range(1, 13))

# Feature engineering
FEATURE_COLS = os.getenv("FEATURE_COLS", "latitude,longitude,depth,mag").split(",")
RAW_FEATURES_COL = os.getenv("RAW_FEATURES_COL", "raw_features")
SCALED_FEATURES_COL = os.getenv("SCALED_FEATURES_COL", "scaled_features")
