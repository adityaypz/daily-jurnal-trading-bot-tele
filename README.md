🚀 Fitur

Menyimpan jurnal trading per hari.

Format catatan rapi (pair, setup, entry, SL, TP, hasil, emosi).

Bisa dipakai sebagai habit tracker untuk trading.

Catatan pribadi (hanya bisa diakses oleh user dengan token bot).

📦 Instalasi

Clone repo ini atau download filenya.

git clone https://github.com/username/trading-journal-bot.git
cd trading-journal-bot


Buat virtual environment (opsional tapi disarankan).

python -m venv venv
source venv/bin/activate    # Linux / Mac
venv\Scripts\activate       # Windows


Install dependency.

pip install -r requirements.txt


Buat bot lewat BotFather di Telegram, lalu ambil API Token.

Simpan token di file .env:

TELEGRAM_BOT_TOKEN=your_api_token_here

▶️ Cara Menjalankan

Jalankan bot dengan:

python bot.py


Kalau mau lebih gampang, kamu juga bisa bikin file run.bat (Windows) atau run.sh (Linux/Mac) untuk sekali klik.

Contoh run.bat:

@echo off
call venv\Scripts\activate
python bot.py
pause

✍️ Format Jurnal

Setiap kali trading, isi jurnal dengan format berikut:

Pair: ETH/USDT
Setup: Breakout 4620
Entry: 4625
SL: 4600
TP: 4660
Hasil: Win (+35 pts)
Emosi: Tenang, percaya diri
Catatan: Volume kuat, trend searah TF besar

📌 Tips Penggunaan

Isi jurnal sebelum entry → tulis rencana.

Tambahkan update setelah trade selesai → catat hasil & emosi.

Evaluasi mingguan: cek kembali semua jurnal → cari pola salah/benar.

👉 Dengan cara ini, bot akan jadi alat self-discipline buat kamu supaya trading lebih terarah dan konsisten.
