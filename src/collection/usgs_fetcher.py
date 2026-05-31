import requests
from pymongo import MongoClient
import calendar
import time
from config.settings import USGS_BASE_URL, USGS_FORMAT, DATA_YEAR, MONTHS, MONGO_URI, MONGO_DB, MONGO_RAW_COL

def fetch_and_store_month(year, month, collection):
    """Fetch data for a single month from USGS API and store directly to MongoDB."""
    last_day = calendar.monthrange(year, month)[1]
    start_time = f"{year}-{month:02d}-01"
    end_time = f"{year}-{month:02d}-{last_day}"
    
    params = {
        "format": USGS_FORMAT, # Menggunakan geojson
        "starttime": start_time,
        "endtime": end_time
    }
    
    for attempt in range(3):
        try:
            print(f"Fetching data for {start_time} to {end_time} (Attempt {attempt+1}/3)...")
            response = requests.get(USGS_BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            
            data_json = response.json()
            features = data_json.get('features', [])
            
            if features:
                # Insert JSON langsung ke MongoDB
                collection.insert_many(features)
                print(f"Bulan {year}-{month:02d}: {len(features)} data berhasil disimpan")
            else:
                print(f"Bulan {year}-{month:02d}: Tidak ada data")
            
            return len(features)
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            time.sleep(2)
            
    print(f"Failed to fetch data for {start_time} to {end_time}")
    return 0

def run_collection():
    """Orchestrate full data collection and direct storage to MongoDB."""
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    collection = db[MONGO_RAW_COL]
    
    total_keseluruhan = 0
    print(f"Memulai pengambilan data gempa tahun {DATA_YEAR}...")
    
    for month in MONTHS:
        total_keseluruhan += fetch_and_store_month(DATA_YEAR, month, collection)
        time.sleep(1) # Delay agar tidak rate limit
        
    print(f"\nProses pengumpulan data selesai.")
    print(f"Total keseluruhan data: {total_keseluruhan}")
    client.close()
