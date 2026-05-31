from pyspark.sql import SparkSession
from config.settings import (
    SPARK_MASTER_URL, SPARK_APP_NAME, SPARK_EXECUTOR_MEM, SPARK_DRIVER_MEM, MONGO_URI
)

_spark = None

def get_spark_session():
    global _spark
    if _spark is None:
        _spark = SparkSession.builder \
            .appName(SPARK_APP_NAME) \
            .master(SPARK_MASTER_URL) \
            .config("spark.executor.memory", SPARK_EXECUTOR_MEM) \
            .config("spark.driver.memory", SPARK_DRIVER_MEM) \
            .config("spark.mongodb.read.connection.uri", MONGO_URI) \
            .config("spark.mongodb.write.connection.uri", MONGO_URI) \
            .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:10.3.0") \
            .getOrCreate()
    return _spark

def stop_spark():
    global _spark
    if _spark:
        _spark.stop()
        _spark = None
