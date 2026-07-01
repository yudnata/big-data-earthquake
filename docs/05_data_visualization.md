# 04 Data Visualization

## Tujuan
Dokumen ini menguraikan arsitektur dan panduan penggunaan dashboard interaktif berbasis Streamlit untuk menyajikan dan mengeksplorasi hasil dari Model Clustering spasial dan hazard gempa bumi global (EMSC) tahun 2025.

## Deskripsi
Dashboard ini dikembangkan menggunakan **Streamlit**, **Folium**, dan **Plotly** dengan tema White Mode (Light Theme) yang premium dan berkecepatan tinggi.

### Struktur Halaman Dashboard
Aplikasi di dalam berkas [visualization/app.py](file:///c:/Users/yudhi/Documents/PROJECT/big-data/visualization/app.py) dibagi menjadi 3 halaman utama:

1. **📊 Ringkasan & Tren Seismik (General Metrics)**:
   - **KPI Cards**: Menampilkan total kejadian gempa, magnitudo tertinggi, jumlah negara terdampak, dan rata-rata kedalaman.
   - **Top 10 Countries (Plotly Bar Chart)**: Peringkat negara yang paling sering mengalami gempa.
   - **Monthly Trends (Plotly Line Chart)**: Tren perkembangan frekuensi gempa per bulan selama tahun 2025.

2. **🗺️ Peta Zona Rawan Spasial (Ring of Fire)**:
   - Peta global interaktif berbasis **Folium** yang memetakan persebaran titik gempa dan diwarnai berdasarkan `kmeans_cluster` (spasial lokasi `x, y, z`).
   - Ukuran radius marker mewakili kekuatan magnitudo asli secara dinamis.
   - Fitur filter dinamis di sidebar untuk menyaring magnitudo dan kedalaman gempa secara real-time.

3. **⚠️ Peta & Profil Bahaya Gempa (Hazard)**:
   - Peta global interaktif Folium yang diwarnai berdasarkan kelompok bahaya fisik patahan (`hazard_cluster`).
   - **Scatter Plot Plotly (Magnitude vs Depth)** dengan sumbu Y kedalaman yang dibalik (mengarah ke bawah bumi). Ini berguna untuk memvalidasi pemisahan fisik klaster bahaya (Dangkal-Lemah, Dangkal-Kuat, Menengah-Sedang, Dalam-Kuat).

## Prerequisites
- Library pada `requirements.txt` kategori *Visualization* telah terpasang (`streamlit`, `folium`, `plotly`, `pymongo`, `python-dotenv`).
- Koleksi MongoDB Atlas `kmeans_results_emsc` dan `kmeans_hazard_results_emsc` sudah terisi dari hasil eksekusi notebook analysis.

## Cara Menjalankan
Aplikasi visualisasi dijalankan dari terminal dengan perintah:
```bash
cd visualization
streamlit run app.py
```

## Optimasi & Troubleshooting
- **Peta Responsif (Random Sampling)**: Untuk mencegah browser hang akibat me-render puluhan ribu titik marker HTML Folium, aplikasi secara otomatis membatasi render maksimal **3.000 titik sampel acak** per halaman peta. Hal ini menjaga framerate browser tetap tinggi di komputer berspesifikasi rendah.
- **Light Theme**: Tampilan dipaksa menggunakan warna latar belakang putih bersih (`#fcfcfc`) dan sidebar abu-abu terang (`#f7fafc`) menggunakan Custom CSS HTML Markdown di dalam Streamlit agar konsisten dengan White Mode.

