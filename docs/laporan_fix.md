# Laporan Progress Tugas Besar Big Data II

**Mata Kuliah:** Big Data II  
**Dosen Pengampu:** Agus Suarjaya (agussuarjaya@it.unud.ac.id)  
**NIM:** [Isi dengan NIM Anda]  
**Nama:** [Isi dengan Nama Anda]  

---

## BAB I PENDAHULUAN
### 1.1 Latar Belakang
#### 1.1.1 Urgensi Analisis Seismologi
Gempa bumi merupakan salah satu bencana alam dengan daya rusak tertinggi yang sebarannya sangat dipengaruhi oleh aktivitas lempeng tektonik. Dalam era digital, pemantauan dan analisis data seismologi secara komputasional menjadi sangat penting guna memahami pola rambatan energi dan memetakan zona rawan bencana (cincin api). Dengan komputasi *Big Data*, jutaan rekam jejak gempa bumi dapat divisualisasikan secara holistik.

#### 1.1.2 Tantangan Big Data dalam Pemetaan Gempa
Pemrosesan data seismologi global menghadapi kendala masifnya volume data. Pada mulanya, pengumpulan data kerap menggunakan API USGS yang memotong data gempa mikro akibat keterbatasan parameter. Namun, untuk mendapatkan peta batas lempeng murni, proyek ini beralih secara penuh menggunakan data utuh dari *European-Mediterranean Seismological Centre* (EMSC). Penggunaan EMSC memastikan tidak ada bias filter magnitudo, memungkinkan pelacakan spasial lempeng secara presisi tinggi.

### 1.2 Rumusan Masalah
#### 1.2.1 Identifikasi Masalah Pengumpulan Data
Bagaimana merancang arsitektur perangkat lunak yang mampu mengumpulkan data skala besar (puluhan ribu rekaman gempa) dari EMSC API secara otomatis dan persisten tanpa mengalami *timeout* atau pemblokiran *rate-limit* dari peladen utama?

#### 1.2.2 Identifikasi Masalah Pemrosesan Spasial
Bagaimana menstandarisasi fitur geospasial (derajat bujur dan lintang) dari data mentah menjadi metrik spasial *Cartesian* yang valid untuk diproses menggunakan algoritma *Machine Learning Clustering*?

### 1.3 Tujuan
#### 1.3.1 Tujuan Umum
Membangun sebuah *pipeline Big Data* yang terotomatisasi secara *end-to-end* mulai dari akuisisi data, prapemrosesan, hingga penyimpanan untuk tujuan klasterisasi spasial.

#### 1.3.2 Tujuan Khusus
Mengimplementasikan arsitektur *Spark Standalone Multi-Node* di atas *Windows Subsystem for Linux* (WSL), memanfaatkan basis data *cloud* MongoDB Atlas, serta melakukan standardisasi tekstual kawasan geografi Flinn-Engdahl.

### 1.4 Manfaat
#### 1.4.1 Manfaat Teknis (Komputasi)
Proyek ini memberikan pemahaman mendalam secara praktis mengenai implementasi arsitektur *Master-Worker* melintasi dua jaringan perangkat keras terpisah dalam *environment* terdistribusi Apache Spark.

#### 1.4.2 Manfaat Praktis (Geografis)
Hasil dari *pipeline* ini dapat dimanfaatkan oleh praktisi geosains untuk memahami penyebaran sabuk tektonik dan pola interaksi lempeng dunia murni berdasarkan metrik jarak spasial.

---

## BAB II KONFIGURASI DAN SETUP
### 2.1 Arsitektur Sistem
#### 2.1.1 Topologi Jaringan Klaster (Laptop A & B)
Sistem ini dibangun di atas topologi dua perangkat komputasi terpisah (Laptop A dan Laptop B) yang masing-masing menjalankan *Windows Subsystem for Linux* (WSL) Ubuntu. Laptop A bertindak ganda sebagai *Master Node* sekaligus *Worker Node*, sedangkan Laptop B didedikasikan secara penuh sebagai *Worker Node* bantuan guna mengakselerasi komputasi klaster.

![Topologi Klaster Spark](/path/to/placeholder_topologi.jpg)
*Gambar 2.1: Diagram topologi jaringan klaster Spark menunjukkan komunikasi antara Master di Laptop A dan Worker di Laptop B.*

#### 2.1.2 Alur Data (Data Pipeline)
Alur kerja dimulai dari proses *ingestion* menggunakan skrip Python untuk menarik *event* seismik melalui EMSC API. Data tabular dalam *memory* tersebut dikonversi menjadi Spark DataFrame, lalu ditransformasikan dan didistribusikan secara komputasi ke seluruh *worker nodes*. Hasil transformasi akhir disimpan secara persisten menuju *cloud database* MongoDB Atlas.

### 2.2 Konfigurasi Database (MongoDB Atlas Cloud)
#### 2.2.1 Pembuatan Cluster Cloud
Infrastruktur basis data dipindahkan ke layanan awan melalui MongoDB Atlas agar dapat diakses dari kedua mesin secara bersamaan. *Cluster* gratis (*tier M0*) diinisialisasi melalui penyedia layanan AWS dengan penempatan *region* terdekat (Singapura) guna meminimalisasi latensi.

![Pembuatan Cluster Atlas](/path/to/placeholder_atlas_cluster.jpg)
*Gambar 2.2: Antarmuka pembuatan cluster M0 pada *dashboard* MongoDB Atlas.*

#### 2.2.2 Pengaturan Network Access dan Database User
Untuk mengizinkan trafik komputasi dari klaster Spark yang bersifat dinamis, *IP Whitelist* dikonfigurasi terbuka menggunakan blokir `0.0.0.0/0`. Selanjutnya, kredensial pengguna basis data (*username* dan *password*) dibangkitkan secara aman dengan privilese *read/write*.

![Network Access Atlas](/path/to/placeholder_atlas_network.jpg)
*Gambar 2.3: Pengaturan Network Access di MongoDB Atlas yang mengizinkan IP universal (0.0.0.0/0).*

#### 2.2.3 Konfigurasi URI Koneksi PySpark
Koneksi antara ekosistem Spark dan MongoDB difasilitasi melalui Spark MongoDB Connector. Parameter URL (URI) *connection string* dengan *prefix* `mongodb+srv://` dienkapsulasi dan dipanggil secara internal pada metode *DataFrameWriter*.

### 2.3 Konfigurasi Apache Spark (Multi-Node di WSL Ubuntu)
#### 2.3.1 Instalasi Dependensi Linux (Java & Spark Binaries)
Persiapan komputasi dimulai dengan instalasi pustaka inti di subsistem Ubuntu, yakni `openjdk-17-jdk`. Berkas arsip kompresi `spark-3.5.0-bin-hadoop3.tgz` diekstrak ke dalam direktori hierarki `/opt/spark` di sistem operasi Linux.

#### 2.3.2 Pendaftaran Environment Variables
Agar tata perintah Spark global dapat tereksekusi lintas direktori, pendefinisian parameter direktori root seperti `JAVA_HOME` dan `SPARK_HOME` dimasukkan secara permanen ke dalam fail eksekusi `~/.bashrc`.

#### 2.3.3 Modifikasi Jaringan Windows-WSL (Mirrored Mode)
Arsitektur *Network Address Translation* (NAT) bawaan WSL menyebabkan isolasi antarmuka jaringan. Masalah ini diselesaikan dengan konfigurasi `.wslconfig` di OS Host Windows melalui penyematan parameter `networkingMode=mirrored`, yang memaksa WSL membagikan *interface* fisik mesin utama.

![Konfigurasi Mirrored Mode](/path/to/placeholder_wslconfig.jpg)
*Gambar 2.4: Berkas .wslconfig yang mengubah mode jaringan NAT menjadi Mirrored.*

#### 2.3.4 Pembukaan Akses Windows Defender Firewall
Windows Defender secara otomatis memblokir koneksi port terdistribusi. Eksekusi utilitas *PowerShell Administrator* melalui perintah `New-NetFirewallRule` dilakukan guna memberikan otoritas Inbound/Outbound TCP terhadap *port* komunikasi Spark (7077), WebUI (8080), Driver (7078), dan BlockManager (7079).

![Firewall Rule Setup](/path/to/placeholder_firewall.jpg)
*Gambar 2.5: Terminal PowerShell Administrator yang mengeksekusi penambahan aturan pengecualian pada Windows Firewall.*

#### 2.3.5 Inisiasi Node Master dan Worker
*Cluster* Spark berhasil dikolaborasikan dengan menjalankan skrip peluncuran `start-master.sh` di Laptop A, dilanjutkan dengan eksekusi `start-worker.sh spark://[IP_MASTER]:7077` di kedua laptop, dilengkapi alokasi distribusi RAM dan inti prosesor komputasi terdedikasi.

![Spark Web UI Master](/path/to/placeholder_spark_webui.jpg)
*Gambar 2.6: Tampilan Spark Web UI di port 8080 menunjukkan dua worker yang berstatus ALIVE.*

### 2.4 Konfigurasi Lingkungan (Environment Python)
#### 2.4.1 Migrasi File Sistem (Windows ke Linux)
Guna mengatasi penurunan kinerja *read/write* (I/O) saat mengeksekusi operasi data masif yang bersumber dari partisi `/mnt/c/`, seluruh direktori hierarki proyek dievakuasi ke *Home Directory* Linux (`~/big-data`).

#### 2.4.2 Manajemen Virtual Environment
Perangkat lunak Python diisolasi menggunakan metode *virtual environment* (`python3 -m venv ~/spark-env`). Mekanisme ini menjaga agar instalasi *library* seperti `pyspark` dan `ipykernel` tidak bercampur dengan dependensi sistem operasi utama Ubuntu.

#### 2.4.3 Proteksi Variabel Kredensial
Sebuah berkas independen berekstensi `.env` dibangun untuk membungkus variabel kredensial tingkat konfidensial seperti URI koneksi MongoDB Atlas dan konfigurasi spesifik klaster, menghindarkan kebocoran rahasia terhadap penyimpanan kontrol versi (Git).

---

## BAB III DATA COLLECTION
### 3.1 Sumber Data (EMSC API)
#### 3.1.1 Pemilihan Seismicportal.eu
Transisi pengambilan data dilakukan menuju portal *European-Mediterranean Seismological Centre* (EMSC). Algoritma penarikan memanfaatkan kemampuan EMSC yang mempublikasikan daftar gempa utuh tanpa paksaan sensor minimal, memfasilitasi kebutuhan komputasi *Pure Spatial*.

#### 3.1.2 Pemahaman Parameter API
Pengikatan layanan EMSC menggunakan kombinasi argumen URI melalui batasan limitasi penarikan sebesar 20.000 titik, batas tanggal operasi (`start`, `end`), serta pelaporan struktur format berbasis *GeoJSON* (`format=json`).

### 3.2 Strategi Penarikan Data (Data Ingestion)
#### 3.2.1 Pembuatan Jendela Waktu (Time Windows)
Aktivitas seismik global yang membludak seringkali memicu kesalahan HTTP 400 (Batasan *Rate-Limit*). Solusi teknis diterapkan melalui pemotongan iterasi perulangan jendela waktu harian menjadi siklus 15-harian berturut-turut.

#### 3.2.2 Penanganan Kegagalan (Retry Mechanism)
Fungsi kontrol eksepsi bertingkat (*try-except block*) disematkan secara implisit. Algoritma diprogram agar melakukan jeda rekursif (*sleep*) dan pemanggilan ulang manakala lalu lintas konektivitas TCP memutus jabat tangan (*handshake*) ke *server* EMSC.

### 3.3 Struktur Data Mentah (Raw Data)
#### 3.3.1 Parsing Struktur GeoJSON
Respons dari EMSC API berbentuk struktur *GeoJSON* bersarang. Kolom meta diparse melalui pendefinisian kunci `properties` serta translasi nilai geometri dari daftar titik koordinat. Seluruh *collection* matriks lalu ditransisikan menjadi format kerangka data struktur Pandas.

#### 3.3.2 Konversi ke Spark DataFrame
Objek statis Pandas dilarutkan ke dalam ekosistem RDD Spark menggunakan fungsi `spark.createDataFrame()`. Proses ini mendistribusikan beban memori tabel mentah secara merata ke dalam *worker node* klaster untuk siap diproses.

### 3.4 Penyimpanan ke Database (Raw Collection)
#### 3.4.1 Proses Penulisan (Write Operations)
Spark *DataFrameWriter* digunakan dengan parameter mode penulisan spesifik (`mode('append')`). Data hasil *ingestion* ditulis seketika menuju koleksi `raw_earthquakes_emsc` yang bersarang pada awan MongoDB Atlas.

#### 3.4.2 Validasi Data Masuk
Log keluaran menunjukkan total eksekusi puluhan ribu injeksi baris secara paripurna. Validasi dijamin melalui pengecekan antarmuka MongoDB Atlas yang mengonfirmasi bahwa baris-baris dokumen tersimpan dalam format skema ganda BSON.

![MongoDB Atlas Raw Data](/path/to/placeholder_atlas_raw.jpg)
*Gambar 3.1: Antarmuka koleksi MongoDB Atlas menampilkan ratusan ribu dokumen data mentah yang berhasil disimpan.*

---

## BAB IV DATA PREPROCESSING
### 4.1 Ekstraksi dan Pembersihan Fitur Dasar
#### 4.1.1 Seleksi Fitur Geografis
Penyiangan fitur secara agresi difokuskan dengan hanya mengekstrak metrik kuantitatif (*magnitude*) dan pemetaan geografis (*latitude*, *longitude*, *depth*). Fitur administratif EMSC seperti `auth` dan `unid` dimusnahkan guna mengoptimalkan alokasi memori.

#### 4.1.2 Penghapusan Data Kotor (Missing Values)
Metode fungsi `dropna()` Spark dijalankan secara global untuk menjamin validitas titik. Tiap dokumen (*row*) dengan anomali atau atribut spasial tidak lengkap (NaN/Null) diekstraksi dari antrean secara brutal.

### 4.2 Text Cleansing Terbimbing (Flinn-Engdahl Regions)
#### 4.2.1 Pembersihan Prefix dan Suffix
Penyebutan lokasi internasional EMSC memanfaatkan spesifikasi linguistik kawasan Flinn-Engdahl. Pembersihan teks ditenagai eksekusi fungsi Regex *string-replacement* guna melucuti sufiks (misal `REGION`, `ISLANDS`) dan prefiks maritim (`OFFSHORE`).

#### 4.2.2 Custom Rules Mapping Geografis
Pemetaan anomali direkayasa dengan penetapan standardisasi wilayah paksa (*hard-coded pattern*), di mana kawasan kepulauan salju (`SIBERIA`, `KAMCHATKA`) distandarkan sebagai `Russia`, serta perairan antar nusa (`BANDA SEA`, `JAVA SEA`) disatukan dalam domain `Indonesia`.

![Hasil Text Cleansing F-E](/path/to/placeholder_text_cleansing.jpg)
*Gambar 4.1: Keluaran (Output) data tabular yang memperlihatkan kolom negara (Country) sudah bersih dari sufiks dan prefiks.*

### 4.3 Transformasi Geometri Bola Bumi 3D
#### 4.3.1 Masalah Distorsi Peta Datar
Kalkulasi *Euclidean distance* konvensional terbukti memicu kesalahan pembobotan pada klasterisasi kutub akibat distorsi lengkungan. Jarak nyata pergerakan bujur tidak lagi identik seiring pendekatan kutub magnetik (Proyeksi Mercator yang keliru).

#### 4.3.2 Konversi Trigonometri Cartesian
Solusi matematis dikerahkan dengan transformasi trigonometri menggunakan perpustakaan `pyspark.sql.functions`. Koordinat kurva bumi diproses dengan penerapan fungsi *Cos* dan *Sin*, merubah lintang/bujur menjadi tiga metrik absolut (*x, y, z*) pada poros rotasi geometris bola 3 dimensi.

![Trigonometric Output](/path/to/placeholder_trigonometry.jpg)
*Gambar 4.2: Transformasi koordinat bumi lintang/bujur menjadi sumbu kartesian X, Y, Z untuk pengukuran spasial sejati.*

### 4.4 Feature Engineering (Pure Spatial)
#### 4.4.1 Peniadaan StandardScaler
Sebagai terobosan dalam memanipulasi *Pure Spatial Clustering*, konversi vektor unit *Z-score* diabaikan secara total. Memaksakan nilai spasial ke dalam model kurva normal *StandardScaler* akan mendistorsi jari-jari jarak proporsional vektor trigonometri bumi sejati.

#### 4.4.2 Penggabungan Fitur (VectorAssembler)
Fitur murni (*x, y, z*) diekstraksi dari skema primitif menggunakan objek Spark `VectorAssembler`. Hasil gabungan array *features* ini mutlak tidak diintervensi oleh kedalaman (*depth*) maupun kekuatan getaran (*magnitude*), sehingga menghasilkan kalkulasi batas lempeng murni.

### 4.5 Penyimpanan Data Bersih (Clean Collection)
#### 4.5.1 Ekspor ke MongoDB
Skema tabulasi final prapemrosesan dikemas ulang dan diumpan ke dalam metode eksekusi ekspor. Secara utuh, skema tabular yang bersih tersimpan pada koleksi sekunder `clean_earthquakes_emsc` pada *database cloud*.

#### 4.5.2 Verifikasi Akhir Skema
Verifikasi mencatat presisi kebersihan tingkat tinggi. Kolom `features` terkonfirmasi bertipe vektor komposit dan seluruh parameter lainnya siap memasuki pilar inti *Machine Learning* tingkat lanjut.

![MongoDB Clean Data Schema](/path/to/placeholder_atlas_clean.jpg)
*Gambar 4.3: Validasi struktur data bersih di MongoDB menunjukkan eksistensi atribut kartesian (x,y,z).*

---

## BAB V PENUTUP
### 5.1 Kesimpulan Sementara
#### 5.1.1 Evaluasi Arsitektur Multi-Node
Penerapan *Virtual Machine* berbasis Linux WSL yang terkalibrasi melalui fitur isolasi OS terbukti mampu menangani beban jaringan Master-Worker Spark pada 2 buah Laptop Windows. Konfigurasi persisten pada level port Firewall menjadi kunci keandalan komputasi.

#### 5.1.2 Evaluasi Pipeline Data
*Pipeline Ingestion* dan tahap transmutasi prapemrosesan bekerja sangat optimal. Model peralihan sistem operasi data mentah asal API EMSC bertransformasi sempurna melewati kaidah *text cleansing* serta menghasilkan skema murni *Pure Spatial* tingkat tinggi.

### 5.2 Rencana Tindak Lanjut (Next Steps)
#### 5.2.1 Tahap Data Analysis
Keluaran data ini diagendakan untuk melewati kawah Candradimuka komputasional: *Machine Learning Spatial Clustering*. Eksperimentasi akan membedah efektivitas dua raksasa algoritma pengelompokan tak tersupervisi (K-Means versus Bisecting K-Means).

#### 5.2.2 Tahap Visualisasi
Integrasi hasil kalkulasi pemetaan batas lempeng akan diakuisisi ulang dari MongoDB. Selanjutnya, hasil prediksi cincin sabuk api bumi akan dipamerkan melewati instrumen pemetaan *dashboard* grafis lintas titik global *interactive*.

---

**Lampiran**
![Bukti Ping Antar Laptop](/path/to/placeholder_ping.jpg)
*Gambar L.1: Bukti fungsional koneksi `ping` yang menghubungkan terminal Linux WSL antar dua laptop (Laptop A & Laptop B).*

![Firewall Port 7077](/path/to/placeholder_firewall_7077.jpg)
*Gambar L.2: Konfigurasi tingkat lanjut Inbound/Outbound Rules pada Windows Defender guna mengotorisasi lalu lintas peladen Apache Spark.*
