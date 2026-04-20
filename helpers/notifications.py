import streamlit as st
import logging
from datetime import datetime
from typing import List
import requests
import json

logger = logging.getLogger(__name__)

# Your bot token (hardcoded for local testing, will use secrets in production)
BOT_TOKEN = "8076498535:AAGo2kD-uxUn6n2_G0Y6MqbZeLra2DT_yfk"


def notifyAdminsOfNewBooking(
    bookingName: str,
    startTs: datetime,
    endTs: datetime,
    studentName: str,
    studentId: str,
    teleHandle: str,
    phoneNumber: str,
    bookingDescription: str,
) -> None:
    """
    Send Telegram notification to admin.
    Fails silently - doesn't crash the booking if notification fails.
    """
    try:
        # Skip notification if booking end time is more than 24 hours in the past
        # (using generous buffer to handle timezone differences between server and local time)
        from datetime import timedelta
        if endTs < datetime.now() - timedelta(hours=24):
            logger.info("Booking is in the past. Skipping notification.")
            return

        try:
            telegram_secrets = st.secrets["telegram"]
            bot_token = telegram_secrets["bot_token"]
            admin_chat_id = str(telegram_secrets["admin_chat_id"])
        except Exception as e:
            logger.warning(f"Could not read telegram secrets: {e}")
            bot_token = BOT_TOKEN
            admin_chat_id = None

        if not bot_token:
            logger.warning("Telegram bot token not configured. Skipping notification.")
            return

        # Format the message
        message = format_booking_notification(
            bookingName, startTs, endTs, studentName, studentId, 
            teleHandle, phoneNumber, bookingDescription
        )

        # If admin_chat_id is set, send only to that person (testing mode)
        if admin_chat_id:
            try:
                send_telegram_message_by_id(bot_token, admin_chat_id, message)
                logger.info(f"Notification sent to admin chat ID: {admin_chat_id}")
            except Exception as e:
                logger.error(f"Failed to notify admin: {str(e)}")
            return

        # Otherwise, send to all admins from Google Sheets
        from helpers import database
        database.refreshUsers()
        users_df = st.session_state["db"]["users"]
        admins = users_df[users_df["user_type"] == "admin"]

        if len(admins) == 0:
            logger.info("No admins configured for notifications.")
            return

        for email, admin in admins.iterrows():
            tele_handle = admin.get("tele_handle", "")
            if not tele_handle or tele_handle.strip() == "":
                continue
            tele_handle = tele_handle.strip("@")
            try:
                send_telegram_message(bot_token, tele_handle, message)
                logger.info(f"Notification sent to admin: {tele_handle}")
            except Exception as e:
                logger.error(f"Failed to notify {tele_handle}: {str(e)}")

    except Exception as e:
        logger.error(f"Error in notifyAdminsOfNewBooking: {str(e)}")


def send_telegram_message_by_id(bot_token: str, chat_id: str, message: str) -> None:
    """Send a Telegram message using a numeric chat ID."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    response = requests.post(url, json=payload, timeout=10)
    if not response.ok:
        error_data = response.json()
        raise ValueError(f"Telegram API error: {error_data.get('description', 'Unknown error')}")


def send_telegram_message(bot_token: str, user_handle: str, message: str) -> None:
    """
    Send a Telegram message via Bot API.
    Converts @username to actual user ID if needed.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    # Try sending to username first
    payload = {
        "chat_id": f"@{user_handle}",
        "text": message,
        "parse_mode": "HTML"
    }

    response = requests.post(url, json=payload, timeout=10)

    if not response.ok:
        error_data = response.json()
        if "not found" in error_data.get("description", "").lower():
            raise ValueError(f"Telegram user @{user_handle} not found. Make sure they exist and have messaged the bot.")
        raise ValueError(f"Telegram API error: {error_data.get('description', 'Unknown error')}")


def format_booking_notification(
    bookingName: str,
    startTs: datetime,
    endTs: datetime,
    studentName: str,
    studentId: str,
    teleHandle: str,
    phoneNumber: str,
    bookingDescription: str,
) -> str:
    """
    Format the notification message.
    """
    start_str = startTs.strftime("%d %b %Y, %H:%M")
    end_str = endTs.strftime("%d %b %Y, %H:%M")

    message = (
        f"📅 <b>New Booking Submitted</b>\n"
        f"\n"
        f"<b>Booking description:</b> {bookingDescription}\n"
        f"<b>Name:</b> {studentName}\n"
        f"<b>Student ID:</b> {studentId}\n"
        f"<b>Telegram:</b> @{teleHandle}\n"
        f"<b>Phone:</b> {phoneNumber}\n"
        f"\n"
        f"📍 <b>Time Slot</b>\n"
        f"<b>Start:</b> {start_str}\n"
        f"<b>End:</b> {end_str}\n"
        f"\n"
        f"<b>Status:</b> ⏳ Pending Approval\n"
        f"\n"
        f"View in admin dashboard to approve or reject."
    )

    return message

