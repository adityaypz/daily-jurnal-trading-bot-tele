# 📓 Trading Journal Bot

Bot Telegram sederhana untuk mencatat **jurnal trading harian**.

---

## ✨ Fitur
- Menyimpan catatan trading per hari.  
- Format rapi: *pair, setup, entry, SL, TP, hasil, emosi*.  
- Bisa dipakai sebagai habit tracker untuk trading.  
- Catatan pribadi (hanya bisa diakses user dengan token bot).  

---

## ⚙️ Instalasi

1. Clone repo ini atau download filenya:
   ```bash
   git clone https://github.com/username/trading-journal-bot.git
   cd trading-journal-bot
   ```

2. Buat virtual environment (opsional tapi disarankan):
   ```bash
   # Linux / Mac
   python -m venv venv
   source venv/bin/activate

   # Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependency:
   ```bash
   pip install -r requirements.txt
   ```

4. Buat bot lewat **BotFather** di Telegram, lalu ambil API Token.  
   Simpan token di file `.env`:
   ```env
   TELEGRAM_BOT_TOKEN=your_api_token_here
   ```

---

## ▶️ Cara Menjalankan

Jalankan bot dengan:
```bash
python bot.py
```

Kalau mau lebih gampang, bisa bikin file `run.bat` (Windows) atau `run.sh` (Linux/Mac) untuk sekali klik.

**Contoh `run.bat`:**
```bat
@echo off
call venv\Scripts\activate
python bot.py
pause
```

**Contoh `run.sh`:**
```bash
#!/bin/bash
source venv/bin/activate
python bot.py
```

---

## 📝 Catatan
- Pastikan sudah install Python 3.8+  
- Token bot harus dijaga, jangan dishare ke orang lain.  
- Semua catatan disimpan pribadi, hanya bisa diakses lewat bot Telegram masing-masing.
