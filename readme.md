# OCR V3

Project ini adalah sistem OCR untuk mendeteksi Exciter, Power Info, dan mengirim laporan ke Google Spreadsheet.

## ⚙️ Setup

1. Clone repository ini:
   ```bash
   git clone https://github.com/username/ocr-v3.git
   cd ocr-v3
Buat file .env:

cp env.example .env
Lalu edit .env dan isi path credential JSON Anda.

Pastikan file credential TIDAK di-commit.
Masukkan file credential ke folder secrets/ atau root, lalu pastikan .gitignore sudah benar.

Jalankan:

pip install -r requirements.txt
python app.py