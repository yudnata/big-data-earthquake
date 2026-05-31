# 01 Data Collection

## Tujuan
Tahap ini bertujuan untuk mengumpulkan data gempa bumi mentah dari USGS Earthquake API untuk periode tahun yang telah ditentukan dan menyimpannya secara persisten ke dalam MongoDB.

## Deskripsi
Proses pengumpulan data dilakukan dengan mengambil SEMUA field yang disediakan oleh USGS API (sebanyak 22 kolom) tanpa melakukan filter apapun pada tahap awal. Ini memastikan kita memiliki data mentah yang utuh untuk keperluan audit atau ekstraksi fitur tambahan di kemudian hari. Data diambil secara iteratif per bulan untuk mencegah beban berlebih (timeout) pada pemanggilan API, kemudian digabungkan dan disimpan ke dalam koleksi `raw_earthquakes`.

### Parameter API USGS
Berikut adalah tabel parameter yang digunakan untuk melakukan pemanggilan ke USGS API:
| Parameter   | Nilai / Contoh               | Keterangan                                       |
|-------------|------------------------------|--------------------------------------------------|
| `format`    | `csv`                        | Format data balasan dari API                     |
| `starttime` | `2025-01-01`                 | Tanggal mulai pencarian data                     |
| `endtime`   | `2025-01-31`                 | Tanggal akhir pencarian data                     |

### Skema Data (Raw)
Dari proses pemanggilan API, kita mendapatkan 22 field utama:
`time`, `latitude`, `longitude`, `depth`, `mag`, `magType`, `nst`, `gap`, `dmin`, `rms`, `net`, `id`, `updated`, `place`, `type`, `horizontalError`, `depthError`, `magError`, `magNst`, `status`, `locationSource`, `magSource`.

## Prerequisites
- Spark Master URL, Memory, dan URI MongoDB telah di-setup di file `.env`.
- Database MongoDB telah berjalan (port default `27017`).
- Koneksi internet stabil.

## Cara Menjalankan
Proses *data collection* ini diorkestrasi langsung dari `main.py`. Tahap ini akan berjalan otomatis apabila sistem mendeteksi belum ada koleksi `raw_earthquakes` di dalam MongoDB.
```bash
python main.py
```

## Penjelasan Fungsi
- `fetch_month(year, month)`: Menarik data satu bulan dari USGS API dan mengembalikan Pandas DataFrame.
- `fetch_all_months(year)`: Melakukan loop per bulan dan menggabungkan semua DataFrame ke satu DataFrame besar.
- `to_spark_dataframe(pdf)`: Konversi Pandas DataFrame ke Spark DataFrame menggunakan *get_spark_session()*.
- `save_to_mongo()`: Menggunakan PySpark MongoDB Connector untuk menulis data.

## Output
Sistem akan menyimpan dataframe berjumlah ratusan ribu baris (tergantung aktivitas gempa pada tahun tersebut) ke MongoDB di collection `raw_earthquakes`. Log akan mencetak: `Saved <N> records → raw_earthquakes`.

## Troubleshooting
- **API Timeout**: Jika mendapatkan timeout, script sudah memiliki mekanisme *retry* sebanyak 3 kali. Jika tetap gagal, pastikan koneksi atau periksa status USGS API.
- **MongoDB Connection Refused**: Pastikan MongoDB service di local atau server Anda sedang berjalan di `localhost:27017` dan variable `MONGO_URI` sudah sesuai di `.env`.
