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
    Send Telegram notification to all configured admin users.
    Fails silently - doesn't crash the booking if notification fails.
    """
    try:
        # Try to get bot token from secrets first (Streamlit Cloud)
        # Fall back to hardcoded token for local testing
        try:
            bot_token = st.secrets.get("telegram", {}).get("bot_token", BOT_TOKEN)
        except:
            bot_token = BOT_TOKEN

        if not bot_token:
            logger.warning("Telegram bot token not configured. Skipping notification.")
            return

        # Get all admin users
        from helpers import database
        database.refreshUsers()
        users_df = st.session_state["db"]["users"]

        # Filter for admins who should receive notifications
        admins = users_df[users_df["user_type"] == "admin"]

        # Optional: Only notify admins with notify_bookings = "yes"
        # Uncomment if you add a "notify_bookings" column to your Users sheet
        # if "notify_bookings" in admins.columns:
        #     admins = admins[admins["notify_bookings"] == "yes"]

        if len(admins) == 0:
            logger.info("No admins configured for notifications.")
            return

        # Format the message
        message = format_booking_notification(
            bookingName, startTs, endTs, studentName, studentId,
            teleHandle, phoneNumber, bookingDescription
        )

        # Send to each admin
        for email, admin in admins.iterrows():
            tele_handle = admin.get("tele_handle", "")
            if not tele_handle or tele_handle.strip() == "":
                logger.warning(f"Admin {email} has no Telegram handle. Skipping.")
                continue

            # Clean handle (remove @ if present)
            tele_handle = tele_handle.strip("@")

            try:
                send_telegram_message(bot_token, tele_handle, message)
                logger.info(f"Notification sent to admin: {tele_handle}")
            except Exception as e:
                logger.error(f"Failed to notify {tele_handle}: {str(e)}")
                # Continue to next admin, don't crash

    except Exception as e:
        logger.error(f"Error in notifyAdminsOfNewBooking: {str(e)}")
        # Silently fail - don't interrupt the booking process


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
    start_str = startTs.strftime("%d %b, %H:%M")
    end_str = endTs.strftime("%H:%M")

    message = f"""
<b>📅 New Booking Submitted</b>

<b>Booking:</b> {bookingDescription}
<b>Name:</b> {studentName}
<b>Student ID:</b> {studentId}
<b>Telegram:</b> @{teleHandle}
<b>Phone:</b> {phoneNumber}

<b>📍 Time Slot</b>
<b>Start:</b> {start_str}
<b>End:</b> {end_str}

<b>Status:</b> ⏳ Pending Approval

View in admin dashboard to approve or reject.
    """.strip()

    return message

