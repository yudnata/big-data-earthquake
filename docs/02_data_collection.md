# 01 Data Collection

## Tujuan
Tahap ini bertujuan untuk mengumpulkan data gempa bumi mentah dari EMSC (European-Mediterranean Seismological Centre) API untuk periode tahun yang telah ditentukan dan menyimpannya secara persisten ke dalam MongoDB.

## Deskripsi
Proses pengumpulan data dilakukan dengan mengambil *event* gempa bumi yang disediakan oleh EMSC API tanpa melakukan filter magnitudo apapun pada tahap awal. Ini memastikan kita memiliki data mentah yang utuh (termasuk *microearthquakes*) untuk keperluan pemetaan batas lempeng secara presisi di kemudian hari. Data diambil secara iteratif per 15 hari untuk mencegah beban berlebih (*timeout* atau limitasi) pada pemanggilan API, kemudian digabungkan dan disimpan ke dalam koleksi `raw_earthquakes_emsc`.

### Parameter API EMSC
Berikut adalah tabel parameter yang digunakan untuk melakukan pemanggilan ke EMSC API:
| Parameter   | Nilai / Contoh               | Keterangan                                       |
|-------------|------------------------------|--------------------------------------------------|
| `format`    | `json`                       | Format data balasan dari API                     |
| `limit`     | `20000`                      | Batas maksimum data per *request*                |
| `start`     | `2025-01-01`                 | Tanggal mulai pencarian data                     |
| `end`       | `2025-01-15`                 | Tanggal akhir pencarian data                     |

### Skema Data (Raw)
Dari proses pemanggilan API EMSC, struktur data diekstrak dari hirarki GeoJSON (kolom `properties`), yang menghasilkan fitur seperti:
`time`, `auth`, `unid`, `mag`, `magtype`, `evtype`, `lon`, `lat`, `depth`, `flynn_region`.

## Prerequisites
- Spark Master URL, Memory, dan URI MongoDB telah di-setup di file `.env`.
- Database MongoDB telah berjalan (port default `27017`).
- Koneksi internet stabil.

## Cara Menjalankan
Proses *data collection* ini diorkestrasi langsung dari `main.py` atau dijalankan lewat sel *notebook*.
```bash
python main.py
```

## Penjelasan Fungsi
- `fetch_15_days(start_date, end_date)`: Menarik data 15 harian dari EMSC API dan mengembalikan Pandas DataFrame.
- `fetch_emsc_data(year)`: Melakukan loop per 15 hari sepanjang tahun dan menggabungkan semua DataFrame ke satu DataFrame besar.
- `to_spark_dataframe(pdf)`: Konversi Pandas DataFrame ke Spark DataFrame menggunakan *get_spark_session()*.
- `save_to_mongo()`: Menggunakan PySpark MongoDB Connector untuk menulis data.

## Output
Sistem akan menyimpan dataframe berjumlah puluhan ribu hingga ratusan ribu baris ke MongoDB di collection `raw_earthquakes_emsc`.

## Troubleshooting
- **API Timeout/Error 400**: Jika batas penarikan per *request* melebihi batas dari EMSC (maksimal 20.000 data per tarikan), pastikan menggunakan jendela waktu yang kecil (misal 15 hari atau 1 minggu).
- **MongoDB Connection Refused**: Pastikan MongoDB service di local atau server Anda sedang berjalan di `localhost:27017`.
