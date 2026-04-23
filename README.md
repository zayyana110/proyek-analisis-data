# 📊 E-Commerce Data Analysis Dashboard

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

## 📌 Deskripsi Proyek
Proyek ini merupakan hasil analisis data dari **E-Commerce Public Dataset**. Fokus utama dari proyek ini adalah untuk melakukan proses *Data Wrangling*, *Exploratory Data Analysis (EDA)*, serta *Explanatory Analysis* guna mendapatkan wawasan (*insight*) mendalam mengenai:
- Performa penjualan kategori produk (Best & Worst Performing Products).
- Tren pendapatan bulanan perusahaan.
- Profil dan segmentasi pelanggan melalui **Analisis RFM (Recency, Frequency, & Monetary)**.

## 🗂️ Struktur Direktori
```bash
proyek-analisis-data/
├── data/
│   ├── (Seluruh dataset mentah dalam format .csv)
├── dashboard/
│   ├── dashboard.py
│   └── main_data.csv
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt

🌐 Link Dashboard (Streamlit Cloud)
Anda dapat mengakses dashboard interaktif secara langsung melalui tautan berikut:
👉 E-Commerce Analysis Dashboard

🚀 Panduan Menjalankan Secara Lokal
1. Clone Repositori
Langkah pertama, unduh proyek ini ke komputer lokal Anda menggunakan perintah berikut:
Bash
git clone [https://github.com/zayyana110/proyek-analisis-data.git](https://github.com/zayyana110/proyek-analisis-data.git)
cd proyek-analisis-data

2. Instalasi Library
Pastikan Anda memiliki Python (versi 3.9 atau lebih baru). Instal semua dependensi yang dibutuhkan menggunakan pip:
Bash
pip install -r requirements.txt
Atau jika perintah pip tidak ditemukan:
Bash
python -m pip install -r requirements.txt

3. Menjalankan Dashboard
Jalankan perintah berikut pada terminal di dalam direktori utama proyek:
Bash
streamlit run dashboard/dashboard.py
Aplikasi akan secara otomatis terbuka di browser default Anda.

📬 Kontak
Nama: Zayyana Maulida
Email: zayyanamaulida1@gmail.com
ID Dicoding: CDCC466D6X1381