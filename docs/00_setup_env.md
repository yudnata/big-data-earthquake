# 00. Setup Database (MongoDB Local)

Karena proses instalasi *Environment Python* dan *PySpark* sudah dirangkum secara lengkap di file **`01_setup_spark.md`**, dokumen ini dikhususkan untuk panduan menyiapkan *Database* penyimpanannya saja.

Proyek ini memproses dan memfilter ratusan ribu baris data. Oleh karena itu, kita menggunakan MongoDB di komputer sendiri (*local*) agar kecepatannya instan, tanpa *latency* internet, dan tanpa batasan kuota.

## Opsi A: Menggunakan Docker (Sangat Disarankan & Paling Praktis)
Jika Anda sudah memiliki **Docker Desktop** yang menyala di Windows/WSL, Anda cukup menjalankan satu baris perintah ini di terminal WSL:
```bash
docker run -d -p 27017:27017 --name mongodb_local mongo:latest
```
*(Docker akan otomatis mengunduh citra (image) MongoDB dan menjalankannya diam-diam di latar belakang selamanya).*

## Opsi B: Instalasi Windows Manual
Jika Anda tidak mau menggunakan Docker:
1. Kunjungi situs web resmi **MongoDB Community Server**.
2. Unduh *installer* berformat `.msi` untuk Windows.
3. Lakukan instalasi standar dengan menekan tombol (Next > Next).
4. Pastikan *service* MongoDB berjalan di *port default* yaitu `27017`.

## Konfigurasi File `.env`
Agar seluruh kode Python (*fetcher* maupun *PySpark*) mengenali *database* ini, pastikan pengaturan koneksi di file `.env` diisi dengan alamat `localhost`:

```env
# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017
MONGO_DB=earthquake_db
MONGO_RAW_COLLECTION=raw_earthquakes
MONGO_CLEAN_COLLECTION=clean_earthquakes
MONGO_KMEANS_COLLECTION=kmeans_results
MONGO_BISECT_COLLECTION=bisecting_results
```
