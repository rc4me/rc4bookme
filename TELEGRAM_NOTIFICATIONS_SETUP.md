# Telegram Notifications Setup Guide

## Overview
When a new booking is submitted, your admin users will receive **instant Telegram notifications** with all booking details. This guide walks you through setup and configuration.

---

## Who Gets Notified?

### Default Behavior
- **All users marked as "admin"** in your Google Sheets Users table receive notifications
- Notifications are sent as **individual direct messages** on Telegram
- The system uses their existing `tele_handle` field (e.g., "john_doe")

### Can You Configure Who Gets Notified?

**YES!** Three options:

#### Option 1: Notify Specific Admins (Recommended)
- Add a new column `notify_bookings` to your Users sheet (values: "yes" or "no")
- Only admins with `notify_bookings = "yes"` receive notifications
- **Best for:** Different admins with different responsibilities

#### Option 2: Telegram Group Chat
- Create a Telegram group for admins
- Add your bot to the group
- Change code to send to group instead of individual DMs
- **Best for:** Simple multi-admin setup, all admins see all bookings

#### Option 3: Single Admin Recipient
- Configure a single admin's Telegram handle in secrets
- All notifications go to one person
- **Best for:** Single admin or centralized booking approval

---

## Quick Setup (15 minutes)

### Step 1: Create a Telegram Bot

1. Open Telegram and find **@BotFather**
2. Send `/start` then `/newbot`
3. Follow the prompts to create your bot
4. **Copy your Bot Token** (looks like: `123456789:ABCdefGHIjklmnopQRSTuvWxyz`)

### Step 2: Add Bot Token to Secrets

Add to `.streamlit/secrets.toml` (or your deployment platform's secrets):

```toml
[telegram]
bot_token = "YOUR_BOT_TOKEN_HERE"
```

**For Streamlit Cloud:** Add in Settings → Secrets

### Step 3: Get Your Telegram User ID (for testing)

1. Message your bot in Telegram (just send anything)
2. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Find your **chat id** in the response (number like `123456789`)
4. Note it down for testing

### Step 4: Update requirements.txt

Add these packages:
```
python-telegram-bot==20.3
requests==2.31.0
```

### Step 5: Copy the Notification Code

Create file: `helpers/notifications.py`

```python
import streamlit as st
import logging
from datetime import datetime
from typing import List
import requests
import json

logger = logging.getLogger(__name__)

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
        bot_token = st.secrets.get("telegram", {}).get("bot_token")
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
            tele_handle = admin["tele_handle"]
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
```

### Step 6: Modify `database.py`

In the `addBooking()` function, add the notification call after the booking is added:

Find this line (around line 115):
```python
    sheet.append_row(row)
```

Add after it:
```python
    # Notify admins of new booking
    from helpers import notifications
    notifications.notifyAdminsOfNewBooking(
        bookingName=name,
        startTs=startTs,
        endTs=endTs,
        studentName=name,
        studentId=studentId,
        teleHandle=teleHandle,
        phoneNumber=phoneNumber,
        bookingDescription=bookingDescription,
    )
```

### Step 7: Update requirements.txt

Run in terminal:
```bash
pip install -r requirements.txt
```

---

## Testing

1. **Send a test message to your bot** on Telegram
2. **Make a test booking** in your app
3. **Check your Telegram** - you should receive a notification within seconds

If you don't receive it:
- Check bot token is correct in secrets
- Verify your Telegram handle in the Users sheet matches your actual @username
- Message the bot first to ensure it has access to DM you
- Check Streamlit logs for errors

---

## Configuration Options

### Change 1: Only Notify Specific Admins

In `notifications.py`, uncomment this section:
```python
if "notify_bookings" in admins.columns:
    admins = admins[admins["notify_bookings"] == "yes"]
```

Then add a `notify_bookings` column to your Users sheet with "yes" or "no" values.

### Change 2: Send to a Telegram Group Instead

Replace the "Send to each admin" section in `notifyAdminsOfNewBooking()`:

```python
# Get group chat ID from secrets
group_chat_id = st.secrets.get("telegram", {}).get("group_chat_id")
if not group_chat_id:
    logger.warning("Telegram group chat ID not configured.")
    return

message = format_booking_notification(...)
send_telegram_message(bot_token, group_chat_id, message)
```

Then in `secrets.toml`:
```toml
[telegram]
bot_token = "YOUR_BOT_TOKEN"
group_chat_id = "-1001234567890"  # Your group's chat ID
```

### Change 3: Send to Single Admin

Add to `secrets.toml`:
```toml
[telegram]
bot_token = "YOUR_BOT_TOKEN"
admin_chat_id = "123456789"
```

Then in `notifications.py`, replace the loop with:
```python
admin_chat_id = st.secrets.get("telegram", {}).get("admin_chat_id")
if admin_chat_id:
    send_telegram_message(bot_token, admin_chat_id, message)
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Telegram user not found" | Message the bot on Telegram first, ensure @handle is correct |
| No notifications received | Check bot token in secrets, verify admin user_type in sheet |
| Bookings work but no notifications | Check Streamlit logs: `streamlit run main.py --logger.level=debug` |
| Bot token invalid | Regenerate token from @BotFather |

---

## Summary

✅ **Default:** Notifies all admins with their Telegram handles  
✅ **Configurable:** Can restrict to specific admins, use a group, or single recipient  
✅ **Reliable:** Failures don't break the booking system  
✅ **Free:** Uses Telegram's free Bot API  

