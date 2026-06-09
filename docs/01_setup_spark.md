# 01. Panduan Lengkap Instalasi & Setup Cluster PySpark di WSL

Karena tugas ini **mewajibkan penggabungan resource 2 laptop** (True Cluster), kita akan menginstal *Python Virtual Environment* untuk koding sekaligus mesin server *Spark Standalone* untuk menggabungkan CPU-nya. 

Silakan lakukan langkah 1 hingga 5 ini di **KEDUA LAPTOP** (Laptop A dan Laptop B).

## 1. Install WSL & Update Ubuntu
Di PowerShell Windows (Run as Administrator), jalankan:
```powershell
wsl --install
```
*Restart komputer, buat username & password Ubuntu. Buka WSL lalu jalankan:*
```bash
sudo apt update && sudo apt upgrade -y
```

## 2. Install Java & Python
PySpark membutuhkan Java JDK 17, sedangkan kita butuh Python untuk membuat *Virtual Environment*.
```bash
sudo apt install -y openjdk-17-jdk python3 python3-pip python3-venv python3-full
```

## 3. Install Mesin Spark Cluster (Wajib)
Kita harus men-download mesin server utama Spark agar bisa menggabungkan tenaga komputasi 2 laptop.
```bash
wget https://archive.apache.org/dist/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz
sudo tar -xvzf spark-3.5.0-bin-hadoop3.tgz -C /opt/
sudo mv /opt/spark-3.5.0-bin-hadoop3 /opt/spark
```

## 4. Set Environment Variables
Daftarkan Java dan Spark ke sistem agar bisa dipanggil dari mana saja:
```bash
echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> ~/.bashrc
echo 'export SPARK_HOME=/opt/spark' >> ~/.bashrc
echo 'export PATH=$PATH:$JAVA_HOME/bin:$SPARK_HOME/bin:$SPARK_HOME/sbin' >> ~/.bashrc
source ~/.bashrc
```

## 5. Salin Project ke Filesystem Linux & Buat Virtual Environment
Agar VS Code berjalan lebih cepat, tidak lambat mendeteksi Python interpreter, dan terhindar dari warning filesystem, **SANGAT DISARANKAN** untuk menyalin folder project dari Windows ke dalam filesystem asli Linux WSL (`~/`):

1. Jalankan perintah ini di terminal WSL (Ubuntu) untuk menyalin folder project ke direktori home Linux:
   ```bash
   # Untuk Laptop A (Sesuaikan path asal Windows Anda):
   cp -r /mnt/c/Users/yudhi/Documents/PROJECT/big-data ~/big-data
   
   # Untuk Laptop B / Teman Anda (Sesuaikan path asal Windows-nya):
   # cp -r "/mnt/e/Tugas_Kuliah/SEM 6/Bigdata/Gempa/big-data-usgs-earthquake" ~/big-data
   ```

2. Masuk ke direktori project yang baru di dalam filesystem Linux:
   ```bash
   cd ~/big-data
   ```

3. Buat dan aktifkan Virtual Environment Python:
   ```bash
   python3 -m venv ~/spark-env
   source ~/spark-env/bin/activate
   ```

4. Install library requirement project (ditambah `ipykernel` untuk Jupyter Notebook):
   ```bash
   pip install pyspark ipykernel
   pip install -r requirements.txt
   ```


---

## 6. MENYALAKAN CLUSTER (PENGGABUNGAN 2 LAPTOP)
Pastikan Laptop A dan B menggunakan satu Wi-Fi yang sama (atau VPN Tailscale). Ketahui IP Laptop A (misal: `192.168.1.10`) dengan mengetik `hostname -I`. Pastikan file `.env` di kedua laptop menggunakan IP Laptop A ini.

**Langkah di Laptop A (Sebagai Master & Pekerja Utama):**
```bash
start-master.sh --host 192.168.1.10
start-worker.sh spark://192.168.1.10:7077
```

**Langkah di Laptop B (Sebagai Pekerja Bantuan):**
Ketahui IP Laptop B (misal: `192.168.1.11`) dengan mengetik `hostname -I`. Jalankan worker dengan mendefinisikan `--host` IP Laptop B tersebut agar Master dapat mengenali dan mengirim task balik ke Laptop B:
```bash
start-worker.sh spark://192.168.1.10:7077 --host 192.168.1.11
```

**Melihat Hasil Penggabungan:** Buka browser di **`http://192.168.1.10:8080`**. Anda akan melihat **2 Worker** hidup dan nilai *Total Cores* serta *Memory* otomatis menjadi gabungan 2 laptop!

## 7. Mulai Koding di VSCode (Hanya di Laptop A)
Sekarang saatnya Anda sebagai "bos" memerintah *cluster* tersebut:
1. Buka VSCode/Antigravity IDE di Windows Anda.
2. Pastikan sudah menginstal ekstensi **WSL**, **Python**, dan **Jupyter**.
3. Tekan `Ctrl + Shift + P` → Pilih **`WSL: Open Folder in WSL`** (atau ketik `code .` di terminal WSL Anda) → Pilih folder proyek ini.
4. Buka file Jupyter Notebook `notebooks/02_data_preprocessing.ipynb`.
5. Di ujung kanan atas (Pilih Kernel), arahkan ke file Python di *virtual environment* Anda:
   `/home/<nama-user-wsl-anda>/spark-env/bin/python3`
6. Silakan jalankan *Cell*-nya (*Play*)!

---

## 🛠️ TROUBLESHOOTING (PANDUAN MENGATASI ERROR LAPANGAN)

Berikut adalah ringkasan solusi dari kendala yang sering terjadi selama proses setup cluster:

### 1. Terminal WSL Tidak Berwarna & Muncul Simbol `#` (Root User)
* **Gejala**: Teks terminal hanya berwarna putih, diakhiri simbol `#`, dan user tertulis `root@...`.
* **Penyebab**: WSL dibuka melalui PowerShell Windows yang di-run "As Administrator", sehingga otomatis masuk sebagai super user.
* **Solusi**: Jangan gunakan PowerShell Administrator untuk masuk ke WSL. Buka langsung aplikasi **Ubuntu** dari Start Menu Windows agar masuk sebagai user biasa (ditandai dengan simbol `$` dan terminal kembali berwarna).

### 2. Error `Command 'wsl' not found` atau `hostname -I` Tidak Jalan
* **Gejala**: Muncul pesan command not found saat mengetik perintah.
* **Penyebab**: Tertukar antara terminal Windows dan Linux. Perintah `wsl --shutdown` adalah perintah **Windows** (jalankan di PowerShell biasa), sedangkan `hostname -I` adalah perintah **Linux** (jalankan di WSL/Ubuntu).

### 3. Masalah Koneksi Ping / Registrasi Worker yang "Stuck" (Gantung)
* **Gejala**: Saat melakukan `ping <IP_Master>`, terminal menggantung tanpa ada balasan, atau laptop worker (Laptop B) gagal masuk ke daftar worker Master.
* **Penyebab**: Windows Defender Firewall memblokir koneksi masuk, profil Wi-Fi diset ke Public (memblokir koneksi lokal), atau WSL Laptop B masih dalam mode NAT.
* **Solusi A (Mirrored Mode, Set Wi-Fi Private & Buka Firewall)**:
  1. **[Wajib di KEDUA Laptop]** Buat file `C:\Users\<Username>\.wslconfig` di Windows Laptop A & Laptop B berisi:
     ```ini
     [wsl2]
     networkingMode=mirrored
     ```
  2. **[Wajib di KEDUA Laptop]** Matikan WSL dengan menjalankan `wsl --shutdown` di PowerShell Windows agar konfigurasi baru aktif.
  3. **[Wajib di KEDUA Laptop]** Ubah profil jaringan Wi-Fi menjadi **Private** (Settings Windows -> Network & Internet -> Wi-Fi -> klik nama Wi-Fi -> pilih **Private Network**).
  4. Buka **PowerShell Windows** (Run as Administrator) di **Laptop Master (Laptop A)**, jalankan perintah ini untuk membuka port Spark, Driver, Block Manager, & Mongo:
     ```powershell
     New-NetFirewallRule -Name "Allow_Ping" -DisplayName "Allow Ping" -Protocol ICMPv4 -Action Allow
     New-NetFirewallRule -DisplayName "Spark Master" -Direction Inbound -LocalPort 7077 -Protocol TCP -Action Allow
     New-NetFirewallRule -DisplayName "Spark WebUI" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow
     New-NetFirewallRule -DisplayName "Spark Driver" -Direction Inbound -LocalPort 7078 -Protocol TCP -Action Allow
     New-NetFirewallRule -DisplayName "Spark BlockManager" -Direction Inbound -LocalPort 7079 -Protocol TCP -Action Allow
     New-NetFirewallRule -DisplayName "MongoDB" -Direction Inbound -LocalPort 27017 -Protocol TCP -Action Allow
     ```
  5. **[Penting] Inisialisasi SparkSession di Python (Laptop A)** harus menyertakan port driver dan block manager yang konsisten dengan firewall di atas:
     ```python
     spark = SparkSession.builder \
         .appName("EarthquakeAnalysis") \
         .master("spark://192.168.1.10:7077") \
         .config("spark.driver.port", "7078") \
         .config("spark.blockManager.port", "7079") \
         .getOrCreate()
     ```
* **Solusi B (Tailscale)**: Instal **Tailscale** di Windows kedua laptop, login dengan akun yang sama, lalu gunakan IP berawalan `100.x.x.x` milik Laptop A.

### 4. Ekstensi WSL Tidak Muncul di Antigravity IDE (VS Codium)
* **Gejala**: Mencari ekstensi "WSL" di marketplace tidak membuahkan hasil karena editor menggunakan marketplace Open VSX.
* **Solusi A (Membuka via Terminal)**: Masuk ke folder project di WSL, lalu ketik perintah `code .` untuk otomatis menghubungkan editor ke WSL.
* **Solusi B (Ganti Source Marketplace)**: Masuk ke Editor Settings, ganti URL Marketplace menjadi:
  * **Gallery URL**: `https://marketplace.visualstudio.com/_apis/public/gallery`
  * **Item URL**: `https://marketplace.visualstudio.com/items`

### 5. Error `Running cells requires the ipykernel package`
* **Gejala**: Jupyter Notebook tidak mau jalan dan meminta instalasi `ipykernel`.
* **Penyebab**: Kernel Jupyter belum memiliki library kernel penghubung, atau Anda salah memilih interpreter Python bawaan sistem (`/usr/bin/python3`).
* **Solusi**: 
  1. Pastikan virtual environment aktif (`(spark-env)` di kiri prompt).
  2. Instal `ipykernel` di terminal WSL Anda:
     ```bash
     pip install ipykernel
     ```
  3. Di VSCode, ubah kernel (Select Kernel) dan arahkan ke path virtual environment yang benar: `/home/<user-wsl-anda>/spark-env/bin/python3`.

