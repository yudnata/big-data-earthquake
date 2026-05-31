# 02 Data Preprocessing

## Tujuan
Tahap preprocessing bertujuan untuk membersihkan data mentah dari API menjadi data yang siap dipakai oleh model Machine Learning (Clustering), termasuk menyeleksi fitur yang relevan, konversi tipe data, penanganan *missing values*, serta *feature engineering*.

## Deskripsi
Dalam tahap ini, kami melakukan beberapa langkah penting:
1. **Seleksi 7 Kolom Utama**: Hanya memilih kolom `time`, `latitude`, `longitude`, `depth`, `mag`, `place`, dan `type`.
2. **Filter Type**: Hanya mengambil data dengan nilai `type = "earthquake"`, lalu menghapus kolom `type` karena sudah tidak relevan.
3. **Casting & Pembersihan**: Mengubah tipe data menjadi Float/Double dan Timestamp. Menghapus baris yang mengandung missing value pada fitur prediktor dan menghapus baris duplikat.
4. **Filter Batas Logis**:
   - `depth` antara `0` hingga `700` km
   - `mag` antara `-2` hingga `10`
   - Koordinat geografis (`latitude`: -90 s/d 90, `longitude`: -180 s/d 180)
5. **Ekstraksi Negara**: Mengekstrak nama negara (kolom `country`) dengan mengambil kata setelah koma terakhir dari kolom `place`. Contoh: `10 km S of Tokyo, Japan` akan diekstrak menjadi `Japan`.
6. **Feature Engineering**: Menggunakan `VectorAssembler` untuk menyatukan fitur ke dalam kolom `raw_features`, kemudian dinormalisasi menggunakan `StandardScaler` ke dalam kolom `scaled_features`.

## Prerequisites
- Tahap `01_data_collection` telah selesai dijalankan.
- Koleksi `raw_earthquakes` ada di dalam MongoDB.

## Cara Menjalankan
Jalankan file utama. Jika data raw sudah ada, script secara cerdas akan langsung memproses data tersebut menuju preprocessing:
```bash
python main.py
```

## Penjelasan Fungsi
- `clean(df)`: Mengeksekusi seleksi, filter logis, dropna, dropDuplicates, dan cast datatype.
- `extract_country(place_col)`: Mengekstrak teks negara menggunakan operasi split dan trim.
- `build_features(df)`: Menerapkan algoritma VectorAssembler dan StandardScaler pada dataset bersih.
- `summary(df)`: Menghasilkan summary statistik dari dataset sebelum dan sesudah *scaling*.

## Output
Dataset yang telah bersih dan mengandung fitur ter-skalakan (`scaled_features`) akan tersimpan ke dalam koleksi MongoDB dengan nama `clean_earthquakes`. Anda juga akan melihat statistik sebelum dan sesudah yang dicetak ke console terminal.

## Troubleshooting
- **Null di scaled_features**: Pastikan tidak ada data `null` atau `NaN` pada kolom fitur sebelum VectorAssembler berjalan. Handle `handleInvalid="skip"` digunakan untuk mencegah error, namun baris bermasalah akan dibuang.
- **Spark Out of Memory (OOM)**: Atur `SPARK_EXECUTOR_MEM` dan `SPARK_DRIVER_MEM` lebih besar di `.env`.
