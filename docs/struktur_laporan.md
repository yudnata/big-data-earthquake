# Laporan Progress Tugas Besar Big Data II

**Mata Kuliah:** Big Data II  
**Dosen Pengampu:** Agus Suarjaya (agussuarjaya@it.unud.ac.id)  
**NIM:** [Isi dengan NIM Anda]  
**Nama:** [Isi dengan Nama Anda]  

---

## BAB I PENDAHULUAN
### 1.1 Latar Belakang
#### 1.1.1 Urgensi Analisis Seismologi
*(Akan berisi penjelasan mengapa data gempa bumi penting untuk dipantau secara komputasional)*
#### 1.1.2 Tantangan Big Data dalam Pemetaan Gempa
*(Akan berisi penjelasan kendala data masif dan peralihan dari data terpotong (USGS) menjadi data utuh (EMSC) untuk pelacakan spasial murni)*

### 1.2 Rumusan Masalah
#### 1.2.1 Identifikasi Masalah Pengumpulan Data
*(Akan berisi pertanyaan penelitian terkait bagaimana mengumpulkan data skala besar dari API secara otomatis)*
#### 1.2.2 Identifikasi Masalah Pemrosesan Spasial
*(Akan berisi pertanyaan penelitian terkait bagaimana menstandarisasi fitur geospasial menjadi metrik yang valid untuk diproses model ML)*

### 1.3 Tujuan
#### 1.3.1 Tujuan Umum
*(Akan berisi target utama, yakni membangun pipeline big data terotomatisasi secara end-to-end)*
#### 1.3.2 Tujuan Khusus
*(Akan berisi target spesifik implementasi arsitektur Spark Standalone Multi-Node di atas subsistem Linux (WSL), pemanfaatan Docker, dan pembersihan data tekstual geografi Flinn-Engdahl)*

### 1.4 Manfaat
#### 1.4.1 Manfaat Teknis (Komputasi)
*(Akan berisi kegunaan proyek ini dalam mempraktikkan Master-Worker architecture melintasi dua jaringan PC terpisah)*
#### 1.4.2 Manfaat Praktis (Geografis)
*(Akan berisi kegunaan temuan proyek untuk pemahaman penyebaran sabuk tektonik dunia)*

---

## BAB II KONFIGURASI DAN SETUP
### 2.1 Arsitektur Sistem
#### 2.1.1 Topologi Jaringan Klaster (Laptop A & B)
*(Akan berisi diagram topologi fisik 2 laptop Windows yang masing-masing menjalankan mesin virtual WSL Ubuntu, di mana Laptop A bertindak sebagai Master+Worker dan Laptop B sebagai Worker bantuan)*
#### 2.1.2 Alur Data (Data Pipeline)
*(Akan berisi deskripsi alur kerja penarikan data dari API EMSC, transformasi di memori Spark Cluster, dan pemuatan persisten ke MongoDB)*

### 2.2 Konfigurasi Database (MongoDB Atlas Cloud)
#### 2.2.1 Pembuatan Cluster Cloud
*(Akan berisi langkah-langkah mendaftar, memilih *cloud provider*, dan membuat cluster gratis (*tier M0*) di MongoDB Atlas)*
#### 2.2.2 Pengaturan Network Access dan Database User
*(Akan berisi cara mengatur IP Whitelist agar bisa diakses dari mana saja (`0.0.0.0/0`) serta pembuatan kredensial user)*
#### 2.2.3 Konfigurasi URI Koneksi PySpark
*(Akan berisi cara menyambungkan URL *connection string* `mongodb+srv://...` ke dalam Spark MongoDB Connector)*

### 2.3 Konfigurasi Apache Spark (Multi-Node di WSL Ubuntu)
#### 2.3.1 Instalasi Dependensi Linux (Java & Spark Binaries)
*(Akan berisi dokumentasi perintah `apt install openjdk-17-jdk` dan ekstraksi arsip `spark-3.5.0-bin-hadoop3.tgz` ke dalam direktori `/opt/spark` di sistem Ubuntu)*
#### 2.3.2 Pendaftaran Environment Variables (`~/.bashrc`)
*(Akan berisi pengaturan parameter `JAVA_HOME` dan `SPARK_HOME` di sistem Linux agar perintah Spark dapat dikenali secara global)*
#### 2.3.3 Modifikasi Jaringan Windows-WSL (Mirrored Mode)
*(Akan berisi tantangan isolasi IP NAT pada WSL, dan solusinya menggunakan file konfigurasi `.wslconfig` (`networkingMode=mirrored`) di Windows agar kedua laptop bisa saling *ping*)*
#### 2.3.4 Pembukaan Akses Windows Defender Firewall
*(Akan berisi eksekusi skrip `New-NetFirewallRule` di PowerShell Administrator untuk membuka lalu lintas TCP ICMPv4 (Ping), Port Master 7077, WebUI 8080, Driver 7078, BlockManager 7079, dan MongoDB 27017)*
#### 2.3.5 Inisiasi Node Master (Laptop 1) dan Worker (Laptop 2)
*(Akan berisi dokumentasi eksekusi `start-master.sh` di Laptop A dan penembakan `start-worker.sh` di Laptop B menuju `spark://IP_MASTER:7077`, serta alokasi memori/CPU dari masing-masing node)*

### 2.4 Konfigurasi Lingkungan (Environment Python)
#### 2.4.1 Migrasi File Sistem (Windows ke Linux)
*(Akan berisi penjelasan taktis penyalinan folder proyek dari partisi Windows (`/mnt/c/`) ke dalam *Home Directory* Linux (`~/big-data`) guna menghindari penurunan kecepatan *read/write* disk WSL)*
#### 2.4.2 Manajemen Virtual Environment dan *Library*
*(Akan berisi proses pembuatan *sandbox* Python (`python3 -m venv ~/spark-env`) dan instalasi paket-paket seperti `pyspark` dan `ipykernel`)*
#### 2.4.3 Proteksi Variabel Kredensial (.env)
*(Akan berisi pendefinisian variabel sensitif seperti lokasi URI MongoDB dan konfigurasi *collection* secara terpusat)*

---

## BAB III DATA COLLECTION
### 3.1 Sumber Data (EMSC API)
#### 3.1.1 Pemilihan Seismicportal.eu
*(Akan berisi alasan perpindahan (*switch*) dari USGS ke EMSC dan keunggulan cakupan datanya)*
#### 3.1.2 Pemahaman Parameter API
*(Akan berisi tabel parameter penarikan data seperti `limit=20000`, `start`, `end`, dan `format=json`)*

### 3.2 Strategi Penarikan Data (Data Ingestion)
#### 3.2.1 Pembuatan Jendela Waktu (Time Windows)
*(Akan berisi logika *looping* pemotongan rentang waktu per-15 hari untuk menghindari *timeout* dan *rate-limit* dari server EMSC)*
#### 3.2.2 Penanganan Kegagalan (Retry Mechanism)
*(Akan berisi penjelasan blok kode *try-except* yang secara otomatis mengulang penarikan jika koneksi internet terputus)*

### 3.3 Struktur Data Mentah (Raw Data)
#### 3.3.1 Parsing Struktur GeoJSON
*(Akan berisi teknik ekstraksi atribut *dictionary* `properties` dan koordinat spasial dari *response* GeoJSON EMSC menjadi Pandas DataFrame)*
#### 3.3.2 Konversi ke Spark DataFrame
*(Akan berisi proses injeksi data tabular ke memori cluster PySpark untuk didistribusikan ke node worker)*

### 3.4 Penyimpanan ke Database (Raw Collection)
#### 3.4.1 Proses Penulisan (Write Operations)
*(Akan berisi penjelasan mode penulisan ke koleksi `raw_earthquakes_emsc` di MongoDB)*
#### 3.4.2 Validasi Data Masuk
*(Akan berisi screenshot log keberhasilan *script* dan tampilan GUI database MongoDB lokal)*

---

## BAB IV DATA PREPROCESSING
### 4.1 Ekstraksi dan Pembersihan Fitur Dasar
#### 4.1.1 Seleksi Fitur Geografis
*(Akan berisi penjelasan pembuangan metadata yang tidak relevan (seperti `auth`, `unid`) dan hanya menyisakan koordinat spasial serta magnitudo)*
#### 4.1.2 Penghapusan Data Kotor (Missing Values)
*(Akan berisi penyaringan baris-baris kosong (*null/NaN*) yang dapat merusak kalkulasi matematis *Clustering*)*

### 4.2 Text Cleansing Terbimbing (Flinn-Engdahl Regions)
#### 4.2.1 Pembersihan Prefix dan Suffix
*(Akan berisi teknik Regex *string-replacement* untuk melucuti embel-embel teks seperti 'REGION', 'OFFSHORE', 'ISLANDS')*
#### 4.2.2 Custom Rules Mapping Geografis
*(Akan berisi logika standarisasi zona spesifik secara paksa, seperti mengubah wilayah laut nusantara menjadi "Indonesia" dan gugusan salju "Siberia" menjadi "Russia")*

### 4.3 Transformasi Geometri Bola Bumi 3D
#### 4.3.1 Masalah Distorsi Peta Datar
*(Akan berisi penjelasan matematis mengapa mengukur metrik *Euclidean distance* di atas koordinat derajat melengkung (lintang/bujur) akan menghasilkan ukuran yang keliru)*
#### 4.3.2 Konversi Trigonometri Cartesian
*(Akan berisi penerapan rumus pengubahan derajat bumi ke dalam unit vektor 3D (`x, y, z`) menggunakan fungsi *Cosinus* dan *Sinus*)*

### 4.4 Feature Engineering (Pure Spatial)
#### 4.4.1 Peniadaan StandardScaler
*(Akan berisi landasan keilmuan mengapa nilai vektor trigonometri tidak boleh dipaksa berdistribusi normal menggunakan *Z-score scaling*)*
#### 4.4.2 Penggabungan Fitur (VectorAssembler)
*(Akan berisi pemakaian *assembler* untuk merakit array tunggal berisikan `[x, y, z]` murni, tanpa intervensi magnitudo maupun kedalaman gempa)*

### 4.5 Penyimpanan Data Bersih (Clean Collection)
#### 4.5.1 Ekspor ke MongoDB
*(Akan berisi proses penyimpanan dataset yang telah bertransformasi ke koleksi `clean_earthquakes_emsc`)*
#### 4.5.2 Verifikasi Akhir Skema
*(Akan berisi screenshot skema tabular final berisikan kolom fitur `[x, y, z]` yang sudah siap diumpankan ke model ML)*

---

## BAB V PENUTUP
### 5.1 Kesimpulan Sementara
#### 5.1.1 Evaluasi Arsitektur Multi-Node
*(Akan berisi ringkasan keberhasilan implementasi dua laptop (*master-worker*) melintasi jaringan Windows ke dalam environment WSL)*
#### 5.1.2 Evaluasi Pipeline Data
*(Akan berisi rangkuman bahwa data mentah EMSC telah sukses dinormalisasi dan diubah bentuknya menjadi format *Pure Spatial* tingkat lanjut)*

### 5.2 Rencana Tindak Lanjut (Next Steps)
#### 5.2.1 Tahap Data Analysis
*(Akan berisi rencana pelatihan model Machine Learning *Pure Spatial Clustering* dengan membandingkan efisiensi algoritma K-Means dan Bisecting K-Means)*
#### 5.2.2 Tahap Visualisasi
*(Akan berisi rencana penggambaran hasil klaster lempeng dunia ke atas dashboard pemetaan global yang interaktif)*

---
