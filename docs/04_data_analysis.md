# 03 Data Analysis

## Tujuan
Dokumen ini mendeskripsikan kerangka konseptual untuk tahap Analisis Data (*EDA*) dan proses *Pure Spatial Clustering* menggunakan PySpark MLlib. Tujuannya adalah memetakan batas nyata dari cincin api (*Ring of Fire*) dunia hanya dengan berbekal data titik persebaran gempa bumi EMSC.

## Deskripsi
Analisis dibagi menjadi dua pilar: *Exploratory Data Analysis* (EDA) dan *Pure Spatial Machine Learning Modeling*.

### Exploratory Data Analysis (EDA)
EDA berfungsi untuk memahami struktur populasi gempa dari EMSC:
- **Agregasi Geografis**: Mengevaluasi top 10 negara/wilayah paling banyak mengalami gempa, di mana Indonesia mendominasi sebagai Raja Gempa akibat posisinya di atas 3 lempeng utama.
- **Outliers**: Pendeteksian gempa di kedalaman (*depth*) ekstrem menggunakan metrik *descriptive statistics*.

### Pure Spatial Clustering (K-Means)
Model K-Means ditugaskan untuk mempartisi lokasi gempa murni berdasar koordinat ruang (`x, y, z`) tanpa diintervensi oleh besaran `magnitudo` maupun `kedalaman`.
- **Geographical Undersampling**: K-Means memiliki kelemahan *density bias*. Karena jumlah gempa di Indonesia bisa menembus belasan ribu sedangkan negara Afrika hanya ratusan, kita membatasi maksimal titik latih per negara sebanyak 5.000 titik. Hal ini memaksa K-Means belajar memetakan seluruh bumi secara adil.
- **Elbow Method Lanjutan**: Titik "siku" dicari dengan mengevaluasi hingga 15 (*K=16*) klaster. Ini dilakukan karena lempeng tektonik utama bumi jumlahnya lebih dari sekadar angka kecil.
- **Silhouette Score**: Evaluator yang menembus skor impresif (0.76+) berkat dihentikannya penggunaan *StandardScaler* pada geometri bola.

### Evaluasi Bisecting K-Means
- **Bisecting K-Means**: Algoritma komparator ini membelah *cluster* dari atas ke bawah. Meskipun kinerjanya bagus (0.70+), namun masih sedikit di bawah dominasi K-Means konvensional.

## Prerequisites
- Data yang sudah dibersihkan (`clean_earthquakes_emsc`).
- Notebook yang digunakan: `notebooks2/03_data_analysis.ipynb`.

## Rencana Eksekusi (Future Work)
- Meload dataset `clean_earthquakes_emsc` dari MongoDB.
- Menerapkan iterasi algoritma evaluasi (Elbow & Silhouette) dari K=2 hingga K=15.
- Menyimpan ringkasan EDA ke dalam MongoDB collection `eda_summary_emsc`.
- Menyimpan metrik evaluasi model ke `model_metrics_emsc`.
- Menyimpan nilai prediksi pemetaan lempeng ke `kmeans_results_emsc` dan `bisecting_results_emsc`.

## Troubleshooting Konseptual
- **Penyimpanan Hasil Model**: Model MLlib seringkali menghasilkan tipe Spark Vector pada outputnya. Pastikan *array/vector features* tersebut di-*drop* sebelum menyimpan kembali datanya ke MongoDB untuk menghindari *error* format dokumen BSON.
