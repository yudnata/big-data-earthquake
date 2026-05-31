from pyspark.sql.functions import col, trim, split, cos, sin, radians, log1p
from pyspark.sql.types import DoubleType, TimestampType
from config.settings import FEATURE_COLS

def extract_country(place_col):
    """Extract country name from place string (e.g., '10 km S of Tokyo, Japan' -> 'Japan')"""
    return trim(split(place_col, ",").getItem(-1))

def clean(df):
    initial_count = df.count()
    print(f"Initial count: {initial_count}")

    # 1. Select and map from geojson nested structure
    df = df.select(
        (col("properties.time") / 1000).cast(TimestampType()).alias("time"),
        col("geometry.coordinates")[1].alias("latitude"),
        col("geometry.coordinates")[0].alias("longitude"),
        col("geometry.coordinates")[2].alias("depth"),
        col("properties.mag").alias("mag"),
        col("properties.place").alias("place"),
        col("properties.type").alias("type")
    )
    
    # 2. Filter earthquake type
    df = df.filter(col("type") == "earthquake").drop("type")
    
    # 3. Cast types
    df = df.withColumn("latitude", col("latitude").cast(DoubleType())) \
           .withColumn("longitude", col("longitude").cast(DoubleType())) \
           .withColumn("depth", col("depth").cast(DoubleType())) \
           .withColumn("mag", col("mag").cast(DoubleType()))
    
    # 4. Drop missing
    df = df.dropna(subset=["latitude", "longitude", "depth", "mag"])
    
    # 5. Drop duplicates
    df = df.dropDuplicates()
    
    # 6. Filter reasonable values
    df = df.filter((col("depth") >= 0) & (col("depth") <= 700))
    df = df.filter((col("mag") >= -2) & (col("mag") <= 10))
    df = df.filter((col("latitude") >= -90) & (col("latitude") <= 90))
    df = df.filter((col("longitude") >= -180) & (col("longitude") <= 180))
    
    # 7. Extract country from place
    df = df.withColumn("country", extract_country(col("place")))
    
    # 8. ADVANCED PREPROCESSING FOR K-MEANS
    # a. Handle Skewed Depth using Log1p (Magnitude is naturally log-scaled already)
    df = df.withColumn("depth_log", log1p(col("depth")))
    
    # b. Handle Spherical Earth constraint (convert Lat/Lon to Cartesian 3D coordinates)
    # This prevents the boundary issue where -179 and +179 are seen as far apart by K-Means
    df = df.withColumn("lat_rad", radians(col("latitude"))) \
           .withColumn("lon_rad", radians(col("longitude"))) \
           .withColumn("x", cos(col("lat_rad")) * cos(col("lon_rad"))) \
           .withColumn("y", cos(col("lat_rad")) * sin(col("lon_rad"))) \
           .withColumn("z", sin(col("lat_rad"))) \
           .drop("lat_rad", "lon_rad")
    
    # Logging
    final_count = df.count()
    print(f"Cleaned count: {final_count}")
    print(f"Dropped rows: {initial_count - final_count}")
    
    return df

def summary(df):
    """Print descriptive statistics for numeric columns."""
    df.describe().show()
