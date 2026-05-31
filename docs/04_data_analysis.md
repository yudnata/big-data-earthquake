# 03 Data Analysis

## Tujuan
Dokumen ini mendeskripsikan kerangka konseptual untuk tahap Analisis Data dan proses Clustering menggunakan PySpark MLlib. Ini menjelaskan pendekatan ilmiah dalam menentukan pengelompokan (zona) rawan gempa berdasarkan data yang telah di-preprocess.

## Deskripsi
Analisis dibagi menjadi dua bagian: Exploratory Data Analysis (EDA) dan Machine Learning Modeling.

### Exploratory Data Analysis (EDA)
EDA berfungsi untuk memahami distribusi dari magnitudo dan kedalaman gempa. EDA mencakup:
- **Analisis Distribusi Frekuensi**: Frekuensi gempa bumi terhadap tingkat magnitudonya.
- **Korelasi Spasial**: Pemeriksaan sekilas terhadap persebaran koordinat lat/long sebelum dilakukan clustering.
- **Outliers**: Pendeteksian gempa di kedalaman atau skala yang ekstrem meskipun sudah difilter pada batas wajar sebelumnya.

### K-Means Clustering
Model utama yang digunakan adalah K-Means yang mempartisi lokasi gempa ke dalam *K* klaster dengan meminimalkan jarak *within-cluster sum of squares*.
- **Elbow Method**: Digunakan untuk mengevaluasi parameter K terbaik. Kita menghitung *Sum of Squared Errors* (SSE) untuk nilai K yang bervariasi (misal k=2 hingga k=10) dan mencari titik "siku" yang menunjukkan *trade-off* terbaik.
- **Silhouette Score**: Metrik evaluasi sekunder yang menilai seberapa baik sebuah observasi tergabung dengan clusternya sendiri dibandingkan klaster lain.

### Bisecting K-Means Clustering
Sebagai perbandingan algoritma, kita menggunakan Bisecting K-Means, yang bekerja dengan membagi semua data dalam satu klaster secara hierarkis (divisive hierarchical clustering) menggunakan prinsip dasar K-Means biasa. Seringkali metode ini lebih stabil saat menghasilkan ukuran cluster yang berimbang pada dataset yang sangat besar.

## Prerequisites
- Data yang sudah dibersihkan dan memiliki `scaled_features` dari MongoDB (`clean_earthquakes`).

## Rencana Eksekusi (Future Work)
- Meload dataset `clean_earthquakes` dari MongoDB.
- Menerapkan iterasi algoritma evaluasi (Elbow & Silhouette).
- Fitting `KMeansModel` & `BisectingKMeansModel`.
- Menyimpan nilai hasil prediksi ke dalam MongoDB collections: `kmeans_results` dan `bisecting_results`.

## Troubleshooting Konseptual
- **Konvergensi yang Lambat**: Mengingat jumlah iterasi dari algoritma clustering di Spark, optimisasi hyperparameter (seperti `maxIter` dan `tol`) diperlukan jika proses memakan waktu terlalu lama.
- **Penyimpanan Hasil**: Model MLlib seringkali menghasilkan tipe Spark Vector pada outputnya. Pastikan tipe Vector ini di-cast ke standard `ArrayType(DoubleType())` atau List biasa sebelum disimpan ke MongoDB agar format dokumen kompatibel (BSON).
