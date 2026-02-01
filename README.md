# 🧥 Fashion Studio ETL Pipeline

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Status](https://img.shields.io/badge/Status-Completed-green.svg)
![Coverage](https://img.shields.io/badge/Coverage-86%25-brightgreen.svg)

Proyek ini adalah implementasi **End-to-End Data Pipeline** yang dikembangkan sebagai submission untuk kelas **Belajar Fundamental Pemrosesan Data (Dicoding)**.

Fokus utama proyek ini adalah membangun otomatisasi pengolahan data fashion, mulai dari pengambilan data mentah (*scraping*), pembersihan & transformasi, hingga penyimpanan terstruktur ke dalam CSV dan Google Sheets.

---

## 🚀 Fitur Utama

Pipeline ini mencakup tahapan lengkap ETL (*Extract, Transform, Load*):

| Tahapan | Deskripsi |
| :--- | :--- |
| **🕷️ Extract** | Mengambil data produk fashion secara otomatis dari situs target menggunakan teknik parsing HTML (Web Scraping). |
| **🔄 Transform** | Membersihkan data (handling null), konversi tipe data (currency/number), dan standarisasi format agar siap dianalisis. |
| **💾 Load** | Menyimpan hasil akhir ke file **CSV** lokal dan mengunggahnya secara *real-time* ke **Google Sheets** via API. |
| **✅ Testing** | Dilengkapi *Unit Testing* (`pytest`) dan laporan *Code Coverage* untuk menjamin kualitas kode. |

---

## 🛠️ Instalasi & Persiapan

Ikuti langkah-langkah berikut untuk menjalankan proyek di lingkungan lokal (Windows).

### 1. Setup Environment
Pastikan Anda menggunakan terminal (PowerShell/CMD).

```bash
# 1. Clone repository (sesuaikan dengan link repo Anda jika ada)
git clone <repository-url>
cd <nama-folder>

# 2. Buat virtual environment
python -m venv env

# 3. Aktifkan virtual environment
.\env\Scripts\activate

```

### 2. Instalasi Dependencies

Instal seluruh pustaka yang diperlukan:

```bash
pip install -r requirements.txt

```

---

## 📂 Struktur Proyek

Berikut adalah susunan direktori dan file dalam proyek ini:

```text
.
├── tests/                  # Unit testing module
│   ├── test_extract.py     # Test scripts for scraping logic
│   ├── test_load.py        # Test scripts for saving data
│   └── test_transform.py   # Test scripts for data cleaning
├── utils/                  # ETL Utility helper functions
│   ├── extract.py          # Logic for web scraping
│   ├── load.py             # Logic for saving to CSV/Sheets
│   └── transform.py        # Logic for cleaning & formatting data
├── main.py                 # Main entry point to run the pipeline
├── products.csv            # Output data file (generated)
├── requirements.txt        # List of Python dependencies
├── submission.txt          # Submission notes/details
└── README.md               # Project documentation

```

---

## 🏃‍♂️ Menjalankan Pipeline

Untuk menjalankan proses utama ETL (Extract → Transform → Load), jalankan perintah berikut:

```bash
python main.py

```

> **Catatan:** Script ini akan menghasilkan file output `products.csv` di direktori lokal dan memperbarui data di Google Sheets secara otomatis.

---

## 🧪 Pengujian (Testing & Coverage)

Proyek ini menjunjung tinggi kualitas kode dengan *test coverage* di atas 85%.

### Konfigurasi Encoding (Penting untuk Windows)

Sebelum menjalankan tes, atur encoding terminal untuk mendukung karakter emoji/simbol:

```powershell
$env:PYTHONIOENCODING = "utf-8"

```

### Menjalankan Unit Test

Gunakan `pytest` untuk menjalankan seluruh skenario pengujian:

```bash
python -m pytest tests

```

### Cek Code Coverage

Untuk melihat laporan cakupan kode:

```bash
# Menjalankan coverage
coverage run -m pytest tests

# Menampilkan laporan
coverage report -m

```

---

## 📊 Hasil Data

Data yang telah berhasil diproses dan divalidasi dapat diakses secara publik melalui tautan berikut:

🔗 **[Google Sheets - Fashion Studio Data](https://docs.google.com/spreadsheets/d/1TTBCPo8qikB2vx14S3xitJOm6UycqcMnc4ZsyaNr2GQ/edit?gid=0#gid=0)**

---

## 👤 Author

**Septio Yasin Tiaratomo**

* 📧 Email: [septioyasin8@gmail.com](mailto:septioyasin8@gmail.com)
* 💻 Submission: Dicoding Indonesia

---

*Dibuat dengan ❤️ dan ☕*
