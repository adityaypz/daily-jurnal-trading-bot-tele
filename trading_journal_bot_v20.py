
import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any

from zoneinfo import ZoneInfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from telegram import Bot, Update
from telegram.constants import ParseMode

DATA_FILE = "data.json"
TZ = ZoneInfo("Asia/Jakarta")

# ---------------- Storage ----------------
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

# ---------------- Template ----------------
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

# ---------------- Scheduler ----------------
scheduler: AsyncIOScheduler | None = None

def ensure_scheduler() -> AsyncIOScheduler:
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler(timezone=TZ)
        scheduler.start()
    return scheduler

async def send_daily_template(bot: Bot, chat_id: int):
    await bot.send_message(chat_id=chat_id, text=journal_template(), parse_mode=ParseMode.MARKDOWN)

def schedule_daily(bot: Bot, chat_id: int, hour: int, minute: int):
    sch = ensure_scheduler()
    job_id = f"daily_{chat_id}"
    # remove existing
    for job in sch.get_jobs():
        if job.id == job_id:
            job.remove()
    trigger = CronTrigger(hour=hour, minute=minute)
    sch.add_job(send_daily_template, trigger, args=[bot, chat_id], id=job_id)

def clear_schedule(chat_id: int):
    if scheduler is None:
        return
    job_id = f"daily_{chat_id}"
    for job in scheduler.get_jobs():
        if job.id == job_id:
            job.remove()

def restore_schedules(bot: Bot):
    data = load_data()
    for chat_str, info in data.items():
        if isinstance(info, dict) and "time" in info:
            try:
                hour, minute = map(int, info["time"].split(":"))
                schedule_daily(bot, int(chat_str), hour, minute)
            except Exception:
                pass

# ---------------- Command Handlers ----------------
async def handle_start(bot: Bot, chat_id: int):
    text = (
        "Hai! Aku bot Jurnal Trading.\n\n"
        "Perintah:\n"
        "• /daily — kirim template jurnal hari ini\n"
        "• /settime HH:MM — auto-kirim harian (Asia/Jakarta)\n"
        "• /cleartime — matikan pengingat harian\n"
        "• /ping — cek waktu server\n"
    )
    await bot.send_message(chat_id=chat_id, text=text)

async def handle_daily(bot: Bot, chat_id: int):
    await bot.send_message(chat_id=chat_id, text=journal_template(), parse_mode=ParseMode.MARKDOWN)

async def handle_settime(bot: Bot, chat_id: int, args: list[str]):
    if len(args) != 1 or ":" not in args[0]:
        await bot.send_message(chat_id=chat_id, text="Format salah. Contoh: /settime 09:00")
        return
    try:
        hh, mm = args[0].split(":")
        hour = int(hh); minute = int(mm)
        if not (0 <= hour < 24 and 0 <= minute < 60):
            raise ValueError
    except ValueError:
        await bot.send_message(chat_id=chat_id, text="Jam tidak valid. Contoh benar: 09:00 atau 18:30")
        return

    data = load_data()
    s = str(chat_id)
    if s not in data:
        data[s] = {}
    data[s]["time"] = f"{hour:02d}:{minute:02d}"
    save_data(data)

    schedule_daily(bot, chat_id, hour, minute)
    await bot.send_message(chat_id=chat_id, text=f"Siap! Aku akan kirim template setiap hari jam {hour:02d}:{minute:02d} WIB.")

async def handle_cleartime(bot: Bot, chat_id: int):
    data = load_data()
    s = str(chat_id)
    if s in data and "time" in data[s]:
        del data[s]["time"]
        save_data(data)
    clear_schedule(chat_id)
    await bot.send_message(chat_id=chat_id, text="Pengingat harian dimatikan.")

async def handle_ping(bot: Bot, chat_id: int):
    now = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
    await bot.send_message(chat_id=chat_id, text=f"Pong! {now} Asia/Jakarta")

# ---------------- Polling Loop ----------------
async def main():
    # Read token
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token and os.path.exists("token.txt"):
        with open("token.txt", "r", encoding="utf-8") as f:
            token = f.readline().strip()
    if not token:
        raise RuntimeError("Bot token not found. Set TELEGRAM_TOKEN or create token.txt with your token on the first line.")

    bot = Bot(token=token)

    # Restore schedules
    restore_schedules(bot)

    # Long polling
    last_update_id = None
    print("Bot started. Listening for updates...")
    while True:
        try:
            updates = await bot.get_updates(offset=(last_update_id + 1) if last_update_id else None, timeout=30)
            for u in updates:
                last_update_id = u.update_id
                if not u.message or not u.message.text:
                    continue
                text = u.message.text.strip()
                chat_id = u.message.chat_id
                # Parse command
                if text.startswith("/"):
                    parts = text.split()
                    cmd = parts[0].lower()
                    args = parts[1:]
                    if cmd == "/start":
                        await handle_start(bot, chat_id)
                    elif cmd == "/daily":
                        await handle_daily(bot, chat_id)
                    elif cmd == "/settime":
                        await handle_settime(bot, chat_id, args)
                    elif cmd == "/cleartime":
                        await handle_cleartime(bot, chat_id)
                    elif cmd == "/ping":
                        await handle_ping(bot, chat_id)
        except Exception as e:
            # Simple backoff on error
            print("Error in polling:", e)
            await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())
