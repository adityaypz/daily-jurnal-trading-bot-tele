
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo

# --- Config ---
DATA_FILE = "data.json"
TZ = ZoneInfo("Asia/Jakarta")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Storage helpers ---
def load_data() -> Dict[str, Any]:
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_data(data: Dict[str, Any]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- Template ---
def journal_template() -> str:
    return (
        "📓 *JURNAL TRADING HARIAN*\n"
        "\n"
        "🗓️ *Tanggal:* \n"
        "⏰ *Jam Trading:* \n"
        "📊 *Pair:* \n"
        "💰 *Modal Akun:* $\n"
        "🎯 *Target Hari Ini:* $\n"
        "\n"
        "1️⃣ *Setup & Rencana*\n"
        "- Analisa singkat: \n"
        "- Rencana Entry: \n"
        "- SL: \n"
        "- TP: \n"
        "- Risk per trade: $\n"
        "\n"
        "2️⃣ *Eksekusi* (isi setelah posisi ditutup)\n"
        "- Entry price: \n"
        "- Exit price: \n"
        "- Hasil (+/-): $\n"
        "- RR Ratio: \n"
        "\n"
        "3️⃣ *Evaluasi*\n"
        "- Kenapa profit / loss?: \n"
        "- Perasaan saat entry & exit: \n"
        "- Perbaikan besok: \n"
        "\n"
        "4️⃣ *Rekap Hari Ini*\n"
        "- Jumlah trade: \n"
        "- Win: \n"
        "- Loss: \n"
        "- Total P/L: $\n"
        "- Modal akhir: $\n"
        "\n"
        "_Tips: Pakai 🟢 untuk profit dan 🔴 untuk loss._"
    )

# --- Scheduler helpers ---
scheduler: AsyncIOScheduler | None = None

def ensure_scheduler(app):
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler(timezone=TZ)
        scheduler.start()
        logger.info("Scheduler started")

async def send_daily_template(app, chat_id: int):
    try:
        await app.bot.send_message(chat_id=chat_id, text=journal_template(), parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Failed to send template to {chat_id}: {e}")

def schedule_job(app, chat_id: int, hour: int, minute: int):
    ensure_scheduler(app)
    job_id = f"daily_{chat_id}"
    # Remove existing job if any
    for job in scheduler.get_jobs():
        if job.id == job_id:
            job.remove()
    trigger = CronTrigger(hour=hour, minute=minute)
    scheduler.add_job(send_daily_template, trigger, args=[app, chat_id], id=job_id)
    logger.info(f"Scheduled daily template for chat {chat_id} at {hour:02d}:{minute:02d} Asia/Jakarta")

def clear_job(chat_id: int):
    if scheduler is None:
        return
    job_id = f"daily_{chat_id}"
    for job in scheduler.get_jobs():
        if job.id == job_id:
            job.remove()

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Hai! Aku bot Jurnal Trading.\n\n"
        "Perintah:\n"
        "• /daily — kirim template jurnal hari ini\n"
        "• /settime HH:MM — auto-kirim harian (Asia/Jakarta)\n"
        "• /cleartime — matikan pengingat harian\n"
        "• /ping — cek waktu server\n"
    )
    await update.message.reply_text(text)

async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(journal_template(), parse_mode="Markdown")

async def settime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    data = load_data()

    if len(context.args) != 1 or ":" not in context.args[0]:
        await update.message.reply_text("Format salah. Contoh: /settime 09:00")
        return

    try:
        hh, mm = context.args[0].split(":")
        hour = int(hh)
        minute = int(mm)
        if not (0 <= hour < 24 and 0 <= minute < 60):
            raise ValueError
    except ValueError:
        await update.message.reply_text("Jam tidak valid. Contoh benar: 09:00 atau 18:30")
        return

    # save time
    str_chat = str(chat_id)
    if str_chat not in data:
        data[str_chat] = {}
    data[str_chat]["time"] = f"{hour:02d}:{minute:02d}"
    save_data(data)

    # schedule
    app = context.application
    schedule_job(app, chat_id, hour, minute)

    await update.message.reply_text(f"Siap! Aku akan kirim template setiap hari jam {hour:02d}:{minute:02d} WIB.")

async def cleartime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    data = load_data()
    str_chat = str(chat_id)

    # remove from data
    if str_chat in data and "time" in data[str_chat]:
        del data[str_chat]["time"]
        save_data(data)

    # clear job
    clear_job(chat_id)
    await update.message.reply_text("Pengingat harian dimatikan.")

def restore_schedules(app):
    data = load_data()
    for chat_str, info in data.items():
        if isinstance(info, dict) and "time" in info:
            try:
                hour, minute = map(int, info["time"].split(":"))
                schedule_job(app, int(chat_str), hour, minute)
            except Exception as e:
                logger.error(f"Failed to restore schedule for {chat_str}: {e}")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
    await update.message.reply_text(f"Pong! {now} Asia/Jakarta")

def read_token() -> str:
    token = os.environ.get("TELEGRAM_TOKEN")
    if token:
        return token.strip()
    # fallback: token.txt
    if os.path.exists("token.txt"):
        with open("token.txt", "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
            if first_line:
                return first_line
    raise RuntimeError("Bot token not found. Set TELEGRAM_TOKEN env var or create token.txt with your token on the first line.")

def main():
    token = read_token()

    app = ApplicationBuilder().token(token).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("daily", daily))
    app.add_handler(CommandHandler("settime", settime))
    app.add_handler(CommandHandler("cleartime", cleartime))
    app.add_handler(CommandHandler("ping", ping))

    # Start scheduler and restore existing schedules
    ensure_scheduler(app)
    restore_schedules(app)

    app.run_polling()

if __name__ == "__main__":
    main()
