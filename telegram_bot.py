"""
Telegram Bot for RC4BookMe - responds to commands:
  /pending  - List all pending (unapproved) bookings
  /start    - Show help message

Run this script separately: python telegram_bot.py
It polls for messages and responds to authorized users.
"""

import os
import requests
import gspread
import json
import time
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

# --- Configuration ---
# Priority: environment variables -> .streamlit/secrets.toml -> hardcoded fallback


BOT_TOKEN = None
ADMIN_CHAT_IDS = []
SERVICE_ACCOUNT_INFO = None

# 1. Try environment variables (used when deployed on Fly.io / Railway etc.)
_env_token = os.environ.get("BOT_TOKEN")
_env_admins = os.environ.get("ADMIN_CHAT_IDS")
_env_sa = os.environ.get("SERVICE_ACCOUNT_JSON")

if _env_token:
    BOT_TOKEN = _env_token
if _env_admins:
    ADMIN_CHAT_IDS = [i.strip() for i in _env_admins.split(",") if i.strip()]
if _env_sa:
    try:
        SERVICE_ACCOUNT_INFO = json.loads(_env_sa)
    except Exception as e:
        logger.error(f"Failed to parse SERVICE_ACCOUNT_JSON env var: {e}")

# 2. Fall back to .streamlit/secrets.toml (used when running locally)
if not BOT_TOKEN or not SERVICE_ACCOUNT_INFO:
    try:
        import toml
        secrets = toml.load(".streamlit/secrets.toml")
        if not BOT_TOKEN:
            BOT_TOKEN = secrets["telegram"]["bot_token"]
        if not ADMIN_CHAT_IDS:
            raw_ids = str(secrets["telegram"]["admin_chat_id"])
            ADMIN_CHAT_IDS = [i.strip() for i in raw_ids.split(",") if i.strip()]
        if not SERVICE_ACCOUNT_INFO:
            SERVICE_ACCOUNT_INFO = dict(secrets["serviceAccount"])
    except Exception:
        pass

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]


def get_spreadsheet():
    """Connect to Google Sheets."""
    sa = gspread.service_account_from_dict(SERVICE_ACCOUNT_INFO, scopes=SCOPE)
    return sa.open("RC4MEDB")


def get_pending_bookings():
    """Fetch all bookings with status 'P' (pending) from Google Sheets."""
    spreadsheet = get_spreadsheet()
    records = spreadsheet.worksheet("Bookings").get_all_records()
    now_ms = datetime.now().timestamp() * 1000
    pending = []
    for r in records:
        if r.get("status") != "P":
            continue
        try:
            end_ms = float(r.get("end_unix_ms", 0))
        except (ValueError, TypeError):
            continue
        if end_ms >= now_ms:
            pending.append(r)
    pending.sort(key=lambda r: float(r.get("start_unix_ms", 0)))
    return pending


def format_pending_message(bookings):
    """Format pending bookings into a readable Telegram message."""
    if not bookings:
        return "✅ No pending bookings! All caught up."

    lines = [f"📋 <b>Pending Bookings ({len(bookings)})</b>\n"]

    for i, b in enumerate(bookings, 1):
        start_ms = b.get("start_unix_ms", 0)
        end_ms = b.get("end_unix_ms", 0)

        if start_ms and end_ms:
            start_dt = datetime.fromtimestamp(float(start_ms) / 1000)
            end_dt = datetime.fromtimestamp(float(end_ms) / 1000)
            start_str = start_dt.strftime("%d %b %Y, %H:%M")
            end_str = end_dt.strftime("%d %b %Y, %H:%M")
        else:
            start_str = f"{b.get('booking_start_date', '?')} {b.get('booking_start_time', '?')}"
            end_str = f"{b.get('booking_end_date', '?')} {b.get('booking_end_time', '?')}"

        name = b.get("name", "Unknown")
        student_id = b.get("student_id", "?")
        tele = b.get("tele_handle", "?")
        phone = b.get("phone_number", "?")
        desc = b.get("booking_description", "No description")

        lines.append(
            f"<b>#{i}</b>\n"
            f"<b>Description:</b> {desc}\n"
            f"<b>Name:</b> {name}\n"
            f"<b>Student ID:</b> {student_id}\n"
            f"<b>Telegram:</b> @{tele}\n"
            f"<b>Phone:</b> {phone}\n"
            f"<b>Time:</b> {start_str} → {end_str}\n"
        )

    lines.append("Go to the admin dashboard to approve or reject.")
    return "\n".join(lines)


def send_message(chat_id, text):
    """Send a message via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    # Telegram has a 4096 char limit per message
    for i in range(0, len(text), 4000):
        chunk = text[i:i+4000]
        payload = {"chat_id": chat_id, "text": chunk, "parse_mode": "HTML"}
        resp = requests.post(url, json=payload, timeout=10)
        if not resp.ok:
            logger.error(f"Failed to send message: {resp.text}")


def poll_bot():
    """Long-poll for Telegram updates and respond to commands."""
    logger.info("Bot started. Polling for messages...")
    offset = 0

    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            params = {"offset": offset, "timeout": 30}
            resp = requests.get(url, params=params, timeout=35)
            data = resp.json()

            for update in data.get("result", []):
                offset = update["update_id"] + 1
                msg = update.get("message", {})
                chat_id = str(msg.get("chat", {}).get("id", ""))
                text = msg.get("text", "").strip()

                # Only respond to authorized admins
                if chat_id not in ADMIN_CHAT_IDS:
                    send_message(chat_id, "⛔ You are not authorized to use this bot.")
                    continue

                if text == "/pending":
                    bookings = get_pending_bookings()
                    reply = format_pending_message(bookings)
                    send_message(chat_id, reply)
                elif text == "/start" or text == "/help":
                    send_message(
                        chat_id,
                        "🤖 <b>RC4BookMe Bot</b>\n\n"
                        "Commands:\n"
                        "/pending - List all pending bookings\n"
                        "/help - Show this message"
                    )
                else:
                    send_message(chat_id, "Unknown command. Use /pending or /help")

        except KeyboardInterrupt:
            logger.info("Bot stopped.")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    if SERVICE_ACCOUNT_INFO is None:
        print("ERROR: Could not load service account.")
        print("Set SERVICE_ACCOUNT_JSON env var or provide .streamlit/secrets.toml with [serviceAccount].")
        exit(1)
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN not set.")
        exit(1)
    if not ADMIN_CHAT_IDS:
        print("ERROR: ADMIN_CHAT_IDS not set.")
        exit(1)
    print(f"Starting bot with {len(ADMIN_CHAT_IDS)} admin(s): {ADMIN_CHAT_IDS}")
    poll_bot()

