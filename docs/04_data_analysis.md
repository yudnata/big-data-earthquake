# 03 Data Analysis

## Tujuan
Dokumen ini mendeskripsikan kerangka konseptual untuk tahap Analisis Data (*EDA*) dan pemodelan *Machine Learning Clustering* menggunakan PySpark MLlib pada dataset EMSC. Terdapat dua notebook yang digunakan untuk membandingkan hasil analisis: pemodelan berbasis lokasi saja (*Pure Spatial Clustering*) dan pemodelan berbasis fisik & koordinat lengkap (*Spatio-Physical & Hazard Profiling*).

## Deskripsi
Analisis dibagi menjadi dua pilar utama: *Exploratory Data Analysis* (EDA) dan *Machine Learning Modeling* (Clustering).

### Exploratory Data Analysis (EDA)
EDA berfungsi untuk memahami struktur populasi gempa dari EMSC:
- **Agregasi Geografis**: Mengevaluasi top 10 negara/wilayah paling banyak mengalami gempa, di mana Indonesia mendominasi sebagai wilayah paling aktif secara seismik akibat posisinya di pertemuan lempeng tektonik utama.
- **Statistik Deskriptif**: Pendeteksian gempa di kedalaman (*depth*) ekstrem dan kekuatan (*magnitude*) menggunakan metrik deskriptif.

### Pemodelan Clustering (K-Means & Bisecting K-Means)
Pemodelan clustering K-Means dilatih menggunakan dua notebook terpisah:

1. **Pemodelan Spasial Murni (Pure Spatial)**:
   - **Notebook**: `notebooks_emsc/03_data_analysis.ipynb`.
   - **Fitur**: Koordinat 3D murni (`x, y, z`) tanpa magnitudo dan kedalaman.
   - **Tujuan**: Memetakan batas cincin api (*Ring of Fire*) murni berdasarkan kedekatan lokasi geografis.

2. **Pemodelan Spasio-Fisik & Profil Bahaya (Spatio-Physical & Earthquake Hazard Profiling)**:
   - **Notebook**: `notebooks_emsc/03_data_analysis_hazard.ipynb`.
   - **Fitur**: `features` (untuk lokasi spasial) dan `hazard_features` (berisi kedalaman logaritmik `depth_log` dan magnitudo `mag` yang telah diskalakan menggunakan `StandardScaler`).
   - **Tujuan**: Memetakan zona rawan bencana sekaligus mengklasifikasikan tingkat kerusakan/bahaya gempa secara global (seperti memisahkan gempa dangkal berdaya rusak tinggi dari gempa dalam yang aman).

## Prerequisites
- Data yang sudah dibersihkan (`clean_earthquakes_emsc`).
- Notebook yang digunakan:
  - `notebooks_emsc/03_data_analysis.ipynb` (Spatial).
  - `notebooks_emsc/03_data_analysis_hazard.ipynb` (Spatio-Physical & Hazard).

## Rencana Eksekusi
- Meload dataset `clean_earthquakes_emsc` dari MongoDB Atlas.
- Menerapkan iterasi evaluasi Elbow Method dan Silhouette Score di kedua notebook.
- Menyimpan hasil klasifikasi klaster spasial dan hazard ke collection MongoDB target:
  - `kmeans_results_emsc` dan `bisecting_results_emsc` (Spatial).
  - Diperbarui dengan kolom tambahan `hazard_cluster` pada versi Spatio-Physical & Hazard.
- Menyimpan ringkasan EDA ke collection `eda_summary_emsc` dan metrik model ke `model_metrics_emsc`.


