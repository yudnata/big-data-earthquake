# Big Data Earthquake Clustering (USGS -> MongoDB -> PySpark Cluster)

Proyek ini merupakan pipeline pengolahan data besar (*Big Data*) untuk mengumpulkan, membersihkan, dan mengelompokkan (melakukan *clustering*) data gempa bumi dunia dari **USGS API** secara real-time. 

Proyek ini didesain khusus menggunakan **PySpark Standalone Cluster** yang menggabungkan sumber daya komputasi dari **2 Laptop** secara nyata (*True Cluster*), dengan **MongoDB** sebagai tempat penyimpanan datanya.

---

## Struktur Project

Semua kode program diletakkan langsung di dalam Jupyter Notebook agar mudah dipresentasikan, dan dokumentasi diatur secara berurutan:

```text
├── docs/                      # Dokumen Panduan Tahapan Project
│   ├── 00_setup_env.md        # Instalasi MongoDB Local / Docker
│   ├── 01_setup_spark.md      # Panduan Instalasi Spark & Cluster 2 Laptop
│   ├── 02_data_collection.md  # Panduan Tahap Pengumpulan Data
│   ├── 03_data_preprocessing.md # Panduan Tahap Pembersihan & Normalisasi Data
│   ├── 04_data_analysis.md    # Panduan Tahap Analisis (K-Means & Bisecting)
│   └── 05_data_visualization.md # Panduan Tahap Visualisasi Dashboard
│
├── notebooks/                 # Jupyter Notebooks (Tempat Kode Utama)
│   ├── 01_data_collection.ipynb     # Pipeline Penarikan Data dari USGS API ke MongoDB
│   ├── 02_data_preprocessing.ipynb  # Pipeline Preprocessing Data di Cluster PySpark
│   └── 03_data_analysis.ipynb       # Pipeline EDA, Elbow Method, K-Means, dan Bisecting K-Means
│
├── .env                       # Konfigurasi Database & Port Spark
├── requirements.txt           # Daftar Library Python yang Dibutuhkan
└── README.md                  # Panduan Utama (File Ini)
```

---

## Langkah Cepat Memulai Project

Silakan ikuti panduan lengkapnya secara berurutan sesuai nomor file di dalam folder `docs/`:

### Tahap 1: Setup Database (MongoDB)
* Dokumen Panduan: [docs/00_setup_env.md](file:///c:/Users/yudhi/Documents/PROJECT/big-data/docs/00_setup_env.md)
* Pastikan MongoDB local Anda sudah berjalan (bisa menggunakan Docker atau instalasi manual `.msi`).
* Pastikan file `.env` di root folder sudah terisi dengan koneksi MongoDB Anda.

### Tahap 2: Setup Cluster PySpark (2 Laptop)
* Dokumen Panduan: [docs/01_setup_spark.md](file:///c:/Users/yudhi/Documents/PROJECT/big-data/docs/01_setup_spark.md)
* Ikuti langkah instalasi Java, Spark, dan Virtual Environment di WSL kedua laptop.
* Hubungkan Laptop B ke Laptop A menggunakan IP Address Master Spark.

### Tahap 3: Pengambilan Data (Jupyter Notebook)
* Jalankan server Jupyter di VSCode (Laptop A).
* Buka dan jalankan seluruh cell di [notebooks/01_data_collection.ipynb](file:///c:/Users/yudhi/Documents/PROJECT/big-data/notebooks/01_data_collection.ipynb) untuk menarik data gempa bumi tahun 2025 ke MongoDB.

### Tahap 4: Preprocessing & Pembersihan Data
* Buka dan jalankan seluruh cell di [notebooks/02_data_preprocessing.ipynb](file:///c:/Users/yudhi/Documents/PROJECT/big-data/notebooks/02_data_preprocessing.ipynb).
* Proses ini akan berjalan di atas PySpark Cluster (menggunakan performa gabungan 2 laptop) untuk membersihkan data, menyaring nama negara menjadi standar internasional, melakukan koordinat kartesius 3D, dan penskalaan fitur.

### Tahap 5: Data Analysis & Clustering
* Buka dan jalankan seluruh cell di [notebooks/03_data_analysis.ipynb](file:///c:/Users/yudhi/Documents/PROJECT/big-data/notebooks/03_data_analysis.ipynb).
* Notebook ini memuat EDA berbasis SparkSQL, visualisasi tren dan distribusi, Elbow Method, K-Means, Bisecting K-Means, serta evaluasi Silhouette Score.
* Hasil tahap ini disimpan terpisah ke MongoDB melalui `eda_summary`, `model_metrics`, `kmeans_results`, dan `bisecting_results`.
* Koleksi hasil cluster hanya menyimpan kolom inti dan label cluster; fitur internal seperti `x`, `y`, `z`, dan `scaled_features` tidak disimpan.
