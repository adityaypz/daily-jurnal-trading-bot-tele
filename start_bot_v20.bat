@echo off
setlocal ENABLEDELAYEDEXPANSION

REM === Always run from this script's directory ===
cd /d "%~dp0"

echo === Trading Journal Bot (v20) Launcher ===

REM === Create venv if missing ===
if not exist "venv\Scripts\python.exe" (
  echo [Setup] Creating virtual environment...
  python -m venv venv
)

REM === Bypass execution policy for this session (PowerShell host) ===
powershell -NoProfile -ExecutionPolicy Bypass -Command "Write-Host 'ExecutionPolicy bypassed for this session.'"

REM === Activate venv ===
call "venv\Scripts\activate"

REM === Upgrade pip and install dependencies ===
echo [Setup] Upgrading pip...
python -m pip install --upgrade pip >nul

echo [Setup] Installing dependencies (python-telegram-bot==20.7, APScheduler==3.10.4, tzdata)...
python -m pip install --no-cache-dir python-telegram-bot==20.7 APScheduler==3.10.4 tzdata >nul

REM === Ensure token.txt exists ===
if not exist "token.txt" (
  echo [ERROR] token.txt not found.
  echo Buat file token.txt dan isi baris pertama dengan token bot dari @BotFather.
  echo Simpan file ini di folder yang sama dengan script.
  pause
  exit /b 1
)

REM === Start the bot ===
echo [Run] Starting bot... (log akan ditulis ke log.txt)
echo Tekan Ctrl+C untuk menghentikan bot.
echo.
python trading_journal_bot_v20.py 1>>log.txt 2>&1

echo.
echo [Stop] Bot berhenti. Lihat log.txt untuk detail.
pause
