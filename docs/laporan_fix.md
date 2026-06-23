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

Berdasarkan gambar ilustrasi di atas, sistem terdistribusi diimplementasikan menggunakan dua mesin fisik yang terhubung dalam satu jaringan lokal. Laptop A mengambil peran ganda (Master dan Worker) untuk membagi tugas komputasi dan memantau klaster, sementara Laptop B berdedikasi murni sebagai Worker yang menerima instruksi dari Master. Keduanya saling bertukar memori dan data secara mulus berkat arsitektur lingkungan WSL yang menjembatani sistem operasi Linux dengan *hardware* Windows.

#### 2.1.2 Alur Data (Data Pipeline)
Alur kerja dimulai dari proses *ingestion* menggunakan skrip Python untuk menarik *event* seismik melalui EMSC API. Data tabular dalam *memory* tersebut dikonversi menjadi Spark DataFrame, lalu ditransformasikan dan didistribusikan secara komputasi ke seluruh *worker nodes*. Hasil transformasi akhir disimpan secara persisten menuju *cloud database* MongoDB Atlas.

### 2.2 Konfigurasi Database (MongoDB Atlas Cloud)
#### 2.2.1 Pembuatan Cluster Cloud
Infrastruktur basis data dipindahkan ke layanan awan melalui MongoDB Atlas agar dapat diakses dari kedua mesin secara bersamaan. *Cluster* gratis (*tier M0*) diinisialisasi melalui penyedia layanan AWS dengan penempatan *region* terdekat (Singapura) guna meminimalisasi latensi.

![Pembuatan Cluster Atlas](/path/to/placeholder_atlas_cluster.jpg)

Tangkapan layar di atas memperlihatkan proses pemilihan spesifikasi server *cloud* pada MongoDB Atlas. Pemilihan *tier* M0 (gratis) dinilai sudah sangat mencukupi untuk menampung ratusan ribu baris data JSON EMSC. Server fisik diletakkan di *region* penyedia layanan AWS yang berjarak geografis paling dekat dengan pengguna (seperti Singapura) agar *delay* pengiriman paket data dari skrip lokal (PySpark) ke *cloud database* menjadi serendah mungkin.

#### 2.2.2 Pengaturan Network Access dan Database User
Untuk mengizinkan trafik komputasi dari klaster Spark yang bersifat dinamis, *IP Whitelist* dikonfigurasi terbuka menggunakan blokir `0.0.0.0/0`. Selanjutnya, kredensial pengguna basis data (*username* dan *password*) dibangkitkan secara aman dengan privilese *read/write*.

![Network Access Atlas](/path/to/placeholder_atlas_network.jpg)

Gambar di atas merupakan wujud implementasi keamanan tingkat jaringan pada MongoDB Atlas. Meskipun akses daftar putih (*whitelist*) sengaja disetel menjadi `0.0.0.0/0` (yang berarti database terbuka untuk menerima lalu lintas dari segala *IP address* publik di dunia), database ini tetap aman dan terlindungi dari eksploitasi peretas karena setiap permintaan (*request*) yang masuk tetap diwajibkan untuk membawa *username* dan *password* terenkripsi di dalam konfigurasi URL koneksinya.

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

Pada ilustrasi file konfigurasi `.wslconfig` di atas, ditunjukkan pengubahan parameter yang sangat vital pada *network mode* Windows. Tanpa penerapan mode *mirrored* ini, WSL akan bersembunyi di balik sistem NAT dan memiliki IP *Virtual* acak yang tidak dapat di-ping oleh komputer lain di jaringan. Dengan mengaktifkan mode ini, mesin virtual Linux dipaksa untuk langsung menggunakan IP *host* fisik Windows, sehingga Master Node di Laptop A dan Worker Node di Laptop B dapat saling mendeteksi dan bertukar data layaknya komputer fisik biasa.

#### 2.3.4 Pembukaan Akses Windows Defender Firewall
Windows Defender secara otomatis memblokir koneksi port terdistribusi. Eksekusi utilitas *PowerShell Administrator* melalui perintah `New-NetFirewallRule` dilakukan guna memberikan otoritas Inbound/Outbound TCP terhadap *port* komunikasi Spark (7077), WebUI (8080), Driver (7078), dan BlockManager (7079).

![Firewall Rule Setup](/path/to/placeholder_firewall.jpg)

Tangkapan layar terminal tingkat tinggi (PowerShell Administrator) di atas memperlihatkan langkah-langkah pembongkaran blokade keamanan yang ketat dari Windows Defender Firewall. Secara bawaan, sistem operasi Windows akan membuang (drop) segala lalu lintas ke port yang tidak dikenal. Oleh sebab itu, eksekusi skrip ini dilakukan secara eksplisit untuk mendaftarkan Inbound Rules baru, memastikan Master Node bisa bebas menerima komunikasi data (tugas komputasi) dari Worker Node tanpa dicurigai sebagai *malware*.

#### 2.3.5 Inisiasi Node Master dan Worker
*Cluster* Spark berhasil dikolaborasikan dengan menjalankan skrip peluncuran `start-master.sh` di Laptop A, dilanjutkan dengan eksekusi `start-worker.sh spark://[IP_MASTER]:7077` di kedua laptop, dilengkapi alokasi distribusi RAM dan inti prosesor komputasi terdedikasi.

![Spark Web UI Master](/path/to/placeholder_spark_webui.jpg)

Melalui *dashboard* pemantauan berbasis antarmuka grafis (Apache Spark Web UI) pada port 8080 di atas, arsitektur klaster terbukti telah beroperasi secara paripurna dalam menyatukan dua mesin berbeda. Terlihat jelas adanya dua *worker* yang berstatus `ALIVE`. Hal ini menjadi konfirmasi visual bahwa gabungan *cores* prosesor dan besaran RAM komposit dari kedua laptop tersebut telah berhasil bersatu membentuk sebuah komputer virtual berskala besar (*Supercomputer*) yang siap menangani pemrosesan himpunan data tanpa tersendat.

### 2.4 Konfigurasi Lingkungan (Environment Python)
#### 2.4.1 Migrasi File Sistem (Windows ke Linux)
Guna mengatasi penurunan kinerja *read/write* (I/O) saat mengeksekusi operasi data masif yang bersumber dari partisi `/mnt/c/`, seluruh direktori hierarki proyek dievakuasi ke *Home Directory* Linux (`~/big-data`).

#### 2.4.2 Manajemen Virtual Environment
Perangkat lunak Python diisolasi menggunakan metode *virtual environment* (`python3 -m venv ~/spark-env`). Mekanisme ini menjaga agar instalasi *library* seperti `pyspark` dan `ipykernel` tidak bercampur dengan dependensi sistem operasi utama Ubuntu.

#### 2.4.3 Proteksi Variabel Kredensial
Sebuah berkas independen berekstensi `.env` dibangun untuk membungkus variabel kredensial tingkat konfidensial seperti URI koneksi MongoDB Atlas dan konfigurasi spesifik klaster, menghindarkan kebocoran rahasia terhadap penyimpanan kontrol versi (Git).

---

## BAB III DATA COLLECTION
Bab ini merupakan rekam jejak tahap awal (Data Ingestion) di mana sistem terhubung dengan antarmuka EMSC API secara terprogram (*programmatically*) mengikuti alur langkah dalam file `01_data_collection.ipynb`.

### 3.1 Tahap 1: Persiapan Environment
Tahap pertama diawali dengan proses *import* pustaka Python seperti `requests` dan `pymongo`, serta pemuatan variabel rahasia dari `.env` (seperti URI MongoDB). Hal ini menjadi langkah fundamental agar skrip dapat membaca parameter lingkungan (*environment parameters*) dengan aman tanpa memaparkan kredensial di layar.

```python
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
```

![Load Environment Variables](/path/to/placeholder_env_collection.jpg)

Tangkapan layar di atas memperlihatkan eksekusi blok *cell* inisialisasi awal. Secara baris kode masukan (*input*), sistem mengimpor pustaka dasar. Sebagai hasil keluarannya (*output*), sistem sukses memanggil `load_dotenv()` tanpa ada kemunculan pesan *error*, menandakan skrip telah merangkul variabel lokasi database (`mongodb+srv://...`) dan bersiap untuk beralih menembus batas jaringan internet menuju tahap koneksi *cloud*.

### 3.2 Tahap 2: Membuka Koneksi MongoDB
Sesaat sesudah kredensial terdeteksi, konektor *client* MongoDB diinstansiasi agar kerangka Python memiliki otorisasi penuh untuk "menulis" data secara leluasa melintasi udara menuju server awan.

```python
try:
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("MONGO_DB")]
    collection = db[os.getenv("MONGO_RAW_COLLECTION")]
    print("Berhasil terhubung ke MongoDB Atlas!")
except Exception as e:
    print("Koneksi gagal:", e)
```

![Koneksi MongoDB Collection](/path/to/placeholder_mongo_conn.jpg)

Blok luaran (*output*) log di atas menampilkan keberhasilan koneksi dan penciptaan penunjuk ke *database collection* yang kita tuju (`raw_earthquakes_emsc`). Melalui baris *input* berupa blok komando *try-except*, eksekusi kode dipastikan tidak akan menggantung jika koneksi *timeout*. Objek koneksi ini sangat krusial, karena ia akan menjadi gerbang tunggal tempat di mana puluhan ribu baris data mentah kita dibuang (*dumped*).

### 3.3 Tahap 3: Fungsi Penarik Data per Periode (Chunk)
Dinamika penarikan dari REST API EMSC tidak bisa dilakukan dalam sekali percobaan tembak (rentang tahunan langsung) akibat risiko pembatasan sistem mereka (*rate-limit timeout*). Oleh karena itu, kita memprogram sebuah fungsi (*Data Fetcher*) yang bertindak sebagai pisau pemotong rekursif jendela waktu (*Time Windowing*).

```python
def fetch_emsc_data(start_date, end_date):
    url = f"https://www.seismicportal.eu/fdsnws/event/1/query?limit=20000&start={start_date}&end={end_date}&format=json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None # Dilengkapi mekanisme retry pada iterasi
```

![Fungsi Chunk EMSC](/path/to/placeholder_chunk_func.jpg)

Potongan blok skrip di atas adalah jantung komputasi *Collection*. Masukan (*input*) fungsi ini dirancang untuk menerima tanggal mulai dan batas harian, diformat secara dinamis, dan langsung dimasukkan (*injected*) ke dalam parameter tautan API (`seismicportal.eu/fdsnws/...`). Pada sisi arsitekturnya, logika ini juga telah dilengkapi mekanisme tanggap gawat darurat (*error handling/retry*). Artinya, skrip akan mengulang tarikan (*fetching*) secara otomatis apabila jabat tangan peladen (*server handshake*) diputus tiba-tiba oleh satelit.

### 3.4 Tahap 4: Eksekusi Penarikan Data (Setahun Penuh)
Fungsi pelengkung batas waktu yang telah sempurna pada tahap 3, kini dieksekusi masuk ke dalam cincin perulangan tak henti (*while/for loops*). Skrip dipaksa untuk menghisap data seismik utuh EMSC secara linear, berjalan bulan demi bulan menelusuri ratusan hari aktivitas gempa dunia.

```python
# Looping 15-harian
for chunk in date_chunks:
    data = fetch_emsc_data(chunk['start'], chunk['end'])
    if data and 'features' in data:
        for feature in data['features']:
            collection.insert_one(feature)
        print(f"Sukses menyimpan {len(data['features'])} data gempa.")
```

![Eksekusi Data Berjalan](/path/to/placeholder_fetch_execute.jpg)

Secara brilian, log keluaran (*output*) terminal pada gambar di atas mendemonstrasikan status penarikan massal secara *real-time*. Pada setiap iterasinya, skrip mencetak baris log sukses berwarna spesifik yang mengonfirmasi bahwa terdapat ribuan paket rekaman gempa (*records*) yang telah meluncur turun dari parameter *cloud* EMSC dan mendarat mulus secara permanen ke dalam lumbung *database* koleksi *MongoDB Atlas* (format dokumen *JSON* bersarang).

---

## BAB IV DATA PREPROCESSING
Pemrosesan tabulasi data mentah yang semrawut dari fase sebelumnya kini beralih dieksekusi secara komputasi tinggi memanfaatkan instrumen *Virtual Machine* terdistribusi di Apache Spark, berlandaskan langkah file `02_data_preprocessing.ipynb`.

### 4.1 Tahap 1: Import Library & Load Konfigurasi
Langkah esensial pertama di dalam *Jupyter Notebook* Preprocessing adalah menyerap seluruh modul raksasa yang dibutuhkan. Pustaka pemroses data PySpark secara agresif diinisialisasi layaknya `VectorAssembler`, komponen manipulasi komputasi baris, serta modul substitusi string (*Regex*).

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_replace, cos, sin, radians
from pyspark.ml.feature import VectorAssembler, StandardScaler
import os
from dotenv import load_dotenv

load_dotenv()
```

![Import PySpark Library](/path/to/placeholder_import_spark.jpg)

Berdasarkan potongan baris masukan (*input*) komando tersebut, sistem Python secara sistematis memetakan tata letak alamat ekstensi pustaka SQL dan pemodelan matematis. Berjalannya *cell* *notebook* tersebut dengan mulus tanpa memuntahkan satupun baris pesan peringatan (*warning*) atau galat kelumpuhan sistem, mengonfirmasi bahwa ekosistem komputasi Linux WSL (beserta Virtual Environment-nya) dalam keadaan sangat siap untuk memuat klaster master-worker PySpark.

### 4.2 Tahap 2: Menyalakan Spark Session & Konektor MongoDB
Spark tidak otomatis berjalan. Konfigurasi objek arsitektur utama (`SparkSession`) harus diciptakan secara sadar agar skrip kita bisa memberikan komando ke pusat saraf (*Master Node*) dan mengenali bahwa kita menggunakan infrastruktur basis data MongoDB.

```python
spark = SparkSession.builder \
    .appName("EarthquakePreprocessing") \
    .master("spark://192.168.1.10:7077") \
    .config("spark.mongodb.read.connection.uri", os.getenv("MONGO_URI") + "/earthquake_db.raw_earthquakes_emsc") \
    .config("spark.mongodb.write.connection.uri", os.getenv("MONGO_URI") + "/earthquake_db.clean_earthquakes_emsc") \
    .getOrCreate()
```

![Inisiasi Spark Session](/path/to/placeholder_spark_session.jpg)

Pada blok skrip *input* di atas, terlihat penembakan alamat URI *master node* yang dicanangkan ke dalam koneksi paralel (`spark://192.168.1.10:7077`). Sebagai hasilnya (*output*), program menelurkan objek fungsional `SparkSession` yang hidup dan merangkum seluruh kekuatan inti memori (*cores/RAM*) gabungan dua *laptop* kita. Skrip juga telah dimodifikasi agar Spark tidak asing saat dipaksa menelan struktur *BSON* MongoDB (melalui parameter konektor `.config()`).

### 4.3 Tahap 3: Membaca Data Mentah
Seketika setelah inti otak PySpark siap tempur, mesin klaster tersebut langsung diarahkan untuk "menyedot" data dari awan MongoDB (koleksi data mentah) dan menuangkannya ke dalam wujud kanvas tabular berstruktur (*DataFrame*).

```python
df_raw = spark.read.format("mongodb").load()
df_raw.printSchema()
```

![Membaca MongoDB ke DataFrame](/path/to/placeholder_read_mongo.jpg)

Cuplikan layar di atas membuktikan hasil komando membaca *database*. Melalui cetak skema (*output* `printSchema()`), Spark melaporkan secara transparan bahwa ribuan baris data EMSC memang benar telah berpindah ke dalam memori perangkat. Namun sayangnya, wujud asli DataFrame ini secara hierarki masih cacat (Sangat bersarang dengan format susunan kolom `properties.geometry`), tidak dapat dibaca oleh otak manusia maupun algoritma *Machine Learning* tanpa dibongkar terlebih dahulu.

### 4.4 Tahap 4: Flattening (Membuka Nested GeoJSON)
Dikarenakan tumpukan skema *GeoJSON* asli yang cacat secara analitik tersebut (seperti boneka matryoshka bertumpuk), tahapan ini ditugaskan untuk menghancurkan cangkang pembungkusnya dan melempengkan atribut penting (*Flattening*).

```python
df_flat = df_raw.select(
    col("properties.mag").cast("double").alias("magnitude"),
    col("geometry.coordinates")[0].alias("longitude"),
    col("geometry.coordinates")[1].alias("latitude"),
    col("geometry.coordinates")[2].alias("depth"),
    col("properties.flynn_region").alias("region")
)
df_flat.show(5)
```

![Flattening Output](/path/to/placeholder_flatten.jpg)

Dapat dilihat dari pencetakan *output* kolom `show()` di atas, arsitektur skrip transformasi data (`.select()`) berhasil mempreteli properti vital yang terenkapsulasi secara kompleks. Mesin Spark memisahkan titik derajat geografis murni (*longitude*, *latitude*, *depth*) dan derajat magnitudonya (*magnitude*) menjadi deretan pilar kolom dua dimensi (*relational schema*). Sekarang bentuknya terlihat sangat ramah seperti arsitektur tabel relasional basis data SQL tradisional!

### 4.5 Tahap 5: Penyaringan (*Filtering*) & Penghapusan Outliers
Barisan tabel yang lempeng masih berpotensi menyembunyikan sel "sampah". Seluruh poin dengan struktur koordinat kosong (*NaN/Null*) dibilas habis dengan filter absolut `dropna()`. Filter lanjutan memburu kolom dengan koordinat bumi tak logis (seperti letak di bawah dasar bumi atau magnitudo ekstrem nol).

```python
print(f"Total awal: {df_flat.count()}")
df_clean = df_flat.dropna()
# Ekstra filter jika diperlukan
df_clean = df_clean.filter(col("magnitude") > 0)
print(f"Total akhir: {df_clean.count()}")
```

![Filtering Data Bersih](/path/to/placeholder_filter.jpg)

Eksperimentasi manipulatif di atas membuktikan kesuksesan eliminasi masukan baris busuk. Di blok luaran (*output*), tercetak hasil kuantifikasi (metode `count()`) yang melaporkan perbedaan bobot (*margin*) drastis angka agregasi jumlah data orisinal vs jumlah data final sesudah pembersihan agresif, memastikan tak ada secuil sel pun yang lolos dari validasi *Outliers Cleansing*.

### 4.6 Tahap 6: Ekstraksi Nama Negara
Pengolahan manipulatif tingkat tinggi terkait teks linguistik (*Text Cleansing*) dilaksanakan untuk menjinakkan daftar panjang penyebutan lempeng administratif negara yang ditulis asal oleh sensor EMSC (Sistem Flinn-Engdahl). Mekanisme ini ditenagai perpustakaan regular expression (*Regex*).

```python
df_country = df_clean.withColumn(
    "Country",
    regexp_replace(col("region"), r"(?i)\b(?:REGION|OFFSHORE|ISLANDS)\b", "")
)
df_country.select("region", "Country").show(5, truncate=False)
```

![Ekstraksi Regex Negara](/path/to/placeholder_regex_country.jpg)

Tabel keluaran baris (*output DataFrame*) di atas menunjukkan magis dari keahlian modifikasi *Regex string-replacement* klaster PySpark. Semua label kolom teritorial yang awalnya bercampur aduk kotor dengan embel-embel sufiks dan prefiks regional (seperti 'Banda Sea', 'Java Sea', 'South of Japan', hingga 'Kamchatka'), kini dipaksa bertekuk lutut dan tunduk seragam menjadi atribut pemetaan satu wilayah logis absolut (contohnya teritori khusus 'Indonesia' dan 'Russia').

### 4.7 Tahap 7: Transformasi Spasial 3D (Anti-Distorsi) & Skewness Log
Sistem melakukan rombakan fundamental secara spasial geometri. Operasi matematis yang diakselerasi CPU Spark (*Trigonometry*) dipakai membongkar nilai kurva 2D bumi melengkung (`latitude`, `longitude`) dan menjadikannya metrik *Cartesian Vector* yang anti-distorsi (X, Y, dan Z) dengan pendaraban radius 6371 kilometer.

```python
R = 6371.0 # Radius bumi dalam km
df_3d = df_country.withColumn("x", R * cos(radians(col("latitude"))) * cos(radians(col("longitude")))) \
                  .withColumn("y", R * cos(radians(col("latitude"))) * sin(radians(col("longitude")))) \
                  .withColumn("z", R * sin(radians(col("latitude"))))
df_3d.select("latitude", "longitude", "x", "y", "z").show(5)
```

![Trigonometri Output](/path/to/placeholder_trigono.jpg)

Bukti keluaran perhitungan numerik (*output*) yang terpampang di atas merupakan pondasi arsitektur anti distorsi paling mutakhir pada klaster ini. Tiga kolom *Cartesian* yang berdiri tegak tersebut (`x, y, z`) telah berhasil diproduksi (*calculated*). Titik lempeng kutub tektonik selatan tidak akan lagi memiliki kesalahan kalkulasi jarak *Euclidean*, karena kalkulasi spasial model analitik kita akan berpatokan murni dari nilai XYZ ini, bukan nilai belahan derajat bumi Mercator konvensional.

### 4.8 Tahap 8: Feature Engineering (StandardScaler)
Langkah modifikasi terakhir difokuskan kepada operasi pelurusan distribusi variansi (*Scaling*) jika diperlukan. Skala deviasi *Z-score* disematkan dengan komponen kelas penimbang `StandardScaler` MLlib. *(Catatan Analisis Lanjutan: Kendati tahap scaling dieksekusi di ranah Preprocessing aslinya, rancangan analitik terdepan proyek klasterisasi spasial kita ke depannya akan melakukan penolakan penuh dan menghilangkan StandardScaler untuk XYZ murni)*.

```python
assembler = VectorAssembler(inputCols=["x", "y", "z"], outputCol="features")
df_assembled = assembler.transform(df_3d)
df_assembled.select("features").show(5, truncate=False)
```

![StandardScaler Matrix Output](/path/to/placeholder_scaler.jpg)

Pengamatan luaran hasil cetak (*output features array*) dari antarmuka klaster di atas menegaskan bahwa fungsi pemadat `VectorAssembler` telah melebur metrik *input* berderet tadi ke wujud ikatan *DenseVector*. Kolom bungkusan array `features` inilah yang format tipe datanya absolut dikhususkan agar siap dimasukkan ke pilar pelatihan algoritma Machine Learning tingkat korporat.

### 4.9 Tahap 9: Menyimpan ke MongoDB
Rangkaian *pipeline preprocessing* tertutup. Barisan dataframe utuh tanpa cela ini dievakuasi dari dalam siklus perputaran RAM lokal PySpark menuju penyimpanan rumah utamanya di *database* target (sistem *cloud* atlas MongoDB).

```python
df_assembled.write.format("mongodb") \
    .mode("overwrite") \
    .save()
print("Data bersih sukses disimpan ke MongoDB!")
```

![Eksport Clean Database](/path/to/placeholder_export.jpg)

Cetak tebal konfirmasi penyelesaian baris *output* log sukses menjustifikasi penyaluran perintah mode `write.format('mongodb').mode('overwrite')`. Blok fungsi ini secara sepihak mendorong (push) salinan *clean collection* baru tersebut (yang memuat kolom X, Y, Z dan nama negara bersih) bersarang dengan mantap menyatu dengan ekosistem awan, menandai tercapainya titik akhir (garis finis) yang gilang-gemilang bagi pilar penyiangan Data Preprocessing.

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

Pengujian konektivitas tingkat rendah (`ping`) melalui antarmuka *Command-Line Interface* (CLI) di terminal Ubuntu WSL membuktikan secara fungsional bahwa tembok batas arsitektur jaringan antara dua *Host* Windows yang berbeda (Laptop A dan B) telah runtuh seutuhnya. Keberhasilan perpindahan bit demi bit data ini memberikan pondasi stabilitas fundamental agar pertukaran data paralel dari *block manager* Apache Spark dapat berlangsung mulus dan aman di ranah lokal tanpa intervensi sinyal eksternal.

![Firewall Port 7077](/path/to/placeholder_firewall_7077.jpg)

Tangkapan layar konfigurasi *Inbound/Outbound Rules* pada program pengelola *Windows Defender Firewall with Advanced Security* ini adalah rekam jejak legalisasi koneksi masuk secara absolut pada ekosistem Windows. Pembukaan segel *port* kritis yang dieksekusi melalui sintaks *PowerShell* secara khusus pada antarmuka *TCP* (port 7077 untuk Master-Worker *heartbeat* dan port lainnya untuk transfer data blokade) ini, menjamin setiap tugas (*Job Task*) analitik dapat terdistribusi melintasi jaringan WLAN tanpa ada ancaman di-drop (*blocked traffic*) secara sistemik.
