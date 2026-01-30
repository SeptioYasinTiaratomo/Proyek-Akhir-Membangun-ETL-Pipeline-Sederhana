Tentu, ini adalah versi `README.md` yang lebih profesional, terstruktur, dan menarik secara visual (menggunakan Markdown) berdasarkan data dan instruksi yang Anda berikan.

Anda bisa menyalin kode di bawah ini dan menyimpannya sebagai file **`README.md`** di folder proyek Anda.

---

```markdown
# 🧥 Fashion Studio ETL Pipeline

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Status](https://img.shields.io/badge/Status-Completed-green.svg)
![Coverage](https://img.shields.io/badge/Coverage-86%25-brightgreen.svg)

Proyek ini merupakan implementasi **End-to-End Data Pipeline** sebagai bagian dari submission kelas **Belajar Fundamental Pemrosesan Data (Dicoding)**.

Fokus utama proyek ini adalah membangun sistem otomatisasi yang mampu mengambil data mentah dari web (scraping), memproses dan membersihkannya (transform), serta menyimpannya ke dalam format yang terstruktur (CSV & Google Sheets) dengan validasi pengujian otomatis.

---

## 👤 Author

* **Nama:** Septio Yasin Tiaratomo
* **Email:** septioyasin8@gmail.com

---

## 🚀 Fitur Utama

Proyek ini mencakup tahapan lengkap ETL (*Extract, Transform, Load*):

* **🕷️ Web Scraping (Extract):** Mengumpulkan data produk fashion secara otomatis dari situs target menggunakan teknik parsing HTML yang efisien.
* **🔄 Data Transformation:** Membersihkan data mentah, menangani nilai yang hilang (null), mengonversi tipe data (mata uang, angka), dan menstandarisasi format agar siap dianalisis.
* **💾 Data Loading:** Menyimpan hasil akhir ke dalam file **CSV** lokal dan mengunggahnya secara *real-time* ke **Google Sheets** menggunakan API.
* **✅ Quality Assurance:** Dilengkapi dengan *Unit Testing* yang komprehensif menggunakan `pytest` dan penanganan *error* (logging) untuk memastikan pipeline berjalan tanpa hambatan.

---

## 🛠️ Instalasi & Persiapan

Ikuti langkah-langkah berikut untuk menjalankan proyek ini di komputer lokal Anda.

### 1. Clone & Setup Environment
Pastikan Anda menggunakan terminal (PowerShell/CMD di Windows).

```bash
# Membuat virtual environment
python -m venv env

# Mengaktifkan environment (Windows)
.\env\Scripts\activate

```

### 2. Instalasi Dependencies

Instal semua pustaka yang dibutuhkan agar skrip berjalan lancar.

```bash
pip install -r requirements.txt

```

*(Opsional) Jika Anda menambahkan library baru, update requirements dengan:*

```bash
pip freeze > requirements.txt

```

---

## 🏃‍♂️ Menjalankan Pipeline

Untuk menjalankan proses ETL utama (Extract -> Transform -> Load):

```bash
python main.py

```

*Script ini akan menghasilkan file `products.csv` dan mengupdate data di Google Sheets.*

---

## 🧪 Pengujian (Testing & Coverage)

Proyek ini menjunjung tinggi kualitas kode. Sebelum menjalankan test, disarankan mengatur encoding terminal agar mendukung karakter khusus (emoji/simbol).

### 1. Setup Encoding (PowerShell)

```powershell
$env:PYTHONIOENCODING = "utf-8"

```

### 2. Menjalankan Unit Test

Anda dapat menggunakan script runner bawaan atau pytest secara langsung:

```bash
# Cara 1: Menggunakan runner manual
python test/run_test.py

# Cara 2: Menggunakan Pytest (Recommended)
python -m pytest tests

```

### 3. Cek Code Coverage

Untuk melihat seberapa banyak kode yang tercover oleh pengujian:

```bash
# Menjalankan coverage
coverage run -m pytest tests

# Melihat laporan hasil (Report)
coverage report -m

```

*Target Coverage: >85%*

---

## 📊 Hasil Data

Data yang berhasil diproses dapat dilihat secara langsung melalui tautan berikut:

🔗 **[Google Sheets - Fashion Studio Data](https://docs.google.com/spreadsheets/d/1TTBCPo8qikB2vx14S3xitJOm6UycqcMnc4ZsyaNr2GQ/edit?gid=0#gid=0)**

---

*Dibuat dengan ❤️ dan ☕ oleh Septio Yasin Tiaratomo*

```

```
