# 02 Data Preprocessing

## Tujuan
Tahap preprocessing bertujuan untuk membersihkan data mentah dari API EMSC menjadi data yang siap dipakai oleh model Machine Learning (*Pure Spatial Clustering*), termasuk konversi tipe data, penanganan *missing values*, serta *text cleansing* nama-nama wilayah geografi Flinn-Engdahl.

## Deskripsi
Dalam tahap ini, kami melakukan beberapa langkah krusial:
1. **Pembersihan Fitur Spasial**: Mengekstrak koordinat lat/lon dari geometri GeoJSON (`properties.lat` & `properties.lon`) dan membuang kolom `type` yang isinya hanya seragam ("earthquake").
2. **Tanpa Filter Magnitudo**: Berbeda dengan versi USGS, pada versi EMSC ini kita *tidak* membuang magnitudo rendah/negatif. Seluruh getaran lempeng sekecil apa pun dipertahankan agar algoritma dapat melacak letak patahan tektonik dengan akurasi maksimal.
3. **Konversi Trigonometri (Fitur 3D)**: Merubah koordinat derajat lintang dan bujur (`latitude`, `longitude`) menjadi koordinat kartesian tiga dimensi (`x`, `y`, `z`) menggunakan rumus sin/cos bola bumi agar metrik jarak K-Means valid secara spasial tanpa mendistorsi bumi jadi bidang datar.
4. **Pembersihan Flinn-Engdahl (Country Extraction)**: 
   - Mengekstrak nama wilayah.
   - Menggunakan *Regex* untuk menghapus *prefix* arah (`NORTH OF`, `OFFSHORE`) dan *suffix* kepulauan (`REGION`, `ISLANDS`).
   - Menyuntikkan aturan kustom (*mapping regex*) untuk mengonversi laut dan semenanjung Rusia (`KAMCHATKA`, `SAKHALIN`, `SIBERIA`) menjadi **Russia**, dan lautan lokal kita (`BALI SEA`, `BANDA SEA`) menjadi **Indonesia**.
5. **Persiapan Pure Spatial Clustering**: Menggunakan `VectorAssembler` *hanya* pada koordinat spasial murni (`x, y, z`). *StandardScaler* secara matematis ditiadakan agar proporsi unit vektor geometri bola bumi tidak hancur akibat *z-score scaling*.

## Prerequisites
- Tahap `01_data_collection` telah selesai dijalankan.
- Koleksi `raw_earthquakes_emsc` ada di dalam MongoDB.

## Cara Menjalankan
Jalankan file utama atau sel-sel di `notebooks2/02_data_preprocessing.ipynb`.

## Output
Dataset yang telah bersih dari cacat teks negara dan berisikan fitur trigonometri 3D (`features`) akan tersimpan ke dalam koleksi MongoDB dengan nama `clean_earthquakes_emsc`. Anda juga akan melihat statistik perubahannya di log.

## Troubleshooting
- **Negara "Aneh"**: Jika ada nama perairan internasional seperti "AEGEAN SEA" atau "MID-ATLANTIC RIDGE" yang tidak menjadi nama negara asli, ini adalah hal yang wajar dalam standar seismologi F-E (netralitas teritorial lautan terbuka).
