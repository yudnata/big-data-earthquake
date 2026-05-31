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

## 5. Buat Virtual Environment Python
Isolasi *library* kodingan Anda agar rapi dan bersih:
```bash
python3 -m venv ~/spark-env
source ~/spark-env/bin/activate

# Install PySpark dan library requirement dari project
pip install pyspark
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
```bash
start-worker.sh spark://192.168.1.10:7077
```

**Melihat Hasil Penggabungan:** Buka browser di **`http://192.168.1.10:8080`**. Anda akan melihat **2 Worker** hidup dan nilai *Total Cores* serta *Memory* otomatis menjadi gabungan 2 laptop!

---

## 7. Mulai Koding di VSCode (Hanya di Laptop A)
Sekarang saatnya Anda sebagai "bos" memerintah *cluster* tersebut:
1. Buka VSCode di Windows Anda.
2. Install ekstensi **WSL**, **Python**, dan **Jupyter** (semuanya buatan Microsoft).
3. Tekan `Ctrl + Shift + P` → Pilih **`WSL: Open Folder in WSL`** → Pilih folder proyek ini.
4. Buka file Jupyter Notebook `notebooks/02_data_preprocessing.ipynb`.
5. Di ujung kanan atas (Pilih Kernel), arahkan ke file Python di *virtual environment* Anda:
   `/home/<nama-user-wsl-anda>/spark-env/bin/python3`
6. Silakan jalankan *Cell*-nya (*Play*)! Spark Master di Laptop A akan secara instan membagi beban data JSON tersebut, mengirimkan setengahnya ke Laptop B, lalu menggabungkannya kembali!
