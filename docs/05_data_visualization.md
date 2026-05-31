# 04 Data Visualization

## Tujuan
Dokumen ini menguraikan desain konseptual dari pembuatan dashboard interaktif berbasis Streamlit untuk menyajikan dan mengeksplorasi hasil dari Model Clustering yang dikembangkan dengan PySpark.

## Deskripsi
Visualisasi difokuskan agar pemangku kepentingan (stakeholder) dan peneliti dapat dengan mudah memantau pembagian zona rawan gempa global dan menelusurinya lebih detail berdasarkan tingkat magnitudo atau kedalaman. 

### Konsep Dashboard (Streamlit)
Dashboard ini nantinya akan bertindak sebagai panel kontrol interaktif yang bisa dijalankan di browser (lokal atau cloud). Elemen utama akan mencakup:
- **Peta Interaktif Geospasial**: Menggunakan *Folium* untuk me-render peta dunia yang ditandai dengan scatter points. Warna akan merepresentasikan kelompok cluster, dan radius menandakan magnitudo gempa.
- **Grafik Distribusi**: Menggunakan *Plotly* dan *Seaborn* untuk menampilkan grafik histogram kedalaman gempa dan bar chart magnitudo berdasar klasifikasi ringan, sedang, dan berat.
- **Heatmap Korelasi**: Memvisualisasikan korelasi numerik antar fitur di dalam klaster tertentu.

### Rencana Filter Interaktif
Pengguna dapat mengubah tampilan peta dengan filter di sisi kiri dashboard:
- Rentang Waktu (Misal: per bulan dalam tahun 2025).
- Batas Magnitudo (Slider dari magnitudo minimal sampai maksimal).
- Rentang Kedalaman.
- Pilih Klaster spesifik (Misal: hanya tampilkan zona Cincin Api/Ring of Fire).

## Prerequisites
- Library pada `requirements.txt` kategori *Visualization & Dashboard* telah terpasang (`streamlit`, `folium`, `plotly`, `matplotlib`, `seaborn`).
- Data prediksi `kmeans_results` atau `bisecting_results` telah tersedia di dalam MongoDB.

## Cara Menjalankan Nanti
Setelah implementasi dilakukan, proses akan dieksekusi dengan menjalankan:
```bash
streamlit run app.py
```

## Troubleshooting Konseptual
- **Peta Lambat Dimuat**: Folium atau peta HTML secara umum memakan resource tinggi jika titik/marker mencapai ratusan ribu (*heavy rendering*). Perlu ada opsi sub-sampling (mengambil max 10.000 titik secara random) untuk UI rendering di Streamlit jika data terlalu besar.
- **Koneksi Database Timeout**: Jika proses Streamlit ke MongoDB lambat, pastikan pembuatan indeks secara spasial atau indeks biasa sudah diterapkan pada database MongoDB agar query pada backend Streamlit merespons di bawah 1 detik.
