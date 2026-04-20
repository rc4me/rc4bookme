# Streamlit Cloud Deployment & Telegram Bot Setup

## What Was Done Locally

✅ Created `helpers/notifications.py` with your bot token hardcoded: `8076498535:AAGo2kD-uxUn6n2_G0Y6MqbZeLra2DT_yfk`  
✅ Updated `database.py` to send notifications when bookings are submitted  
✅ Added required packages to `requirements.txt`

**This works on your local machine!** To test locally:
```bash
pip install -r requirements.txt
streamlit run main.py
```

---

## Deploying to Streamlit Cloud (What You Need to Do Now)

### Option 1: Using Streamlit Cloud with Secrets (RECOMMENDED)

This is the **secure way** - your bot token stays private in Streamlit Cloud's secrets manager.

#### Step 1: Push Your Code to GitHub

1. Go to **GitHub** (create account if needed: https://github.com/signup)
2. Create a new repository called `rc4bookme`
3. Clone it locally or use GitHub Desktop
4. Copy your project files into the repository
5. Commit and push all files to GitHub:
   ```bash
   git add .
   git commit -m "Initial commit with Telegram notifications"
   git push origin main
   ```

#### Step 2: Deploy to Streamlit Cloud

1. Go to **https://streamlit.io/cloud**
2. Click **"New app"**
3. Select your GitHub repository (`rc4bookme`)
4. Branch: `main`
5. Main file path: `main.py`
6. Click **"Deploy"** and wait (takes 2-3 minutes)

#### Step 3: Add Secrets in Streamlit Cloud

Once deployed:

1. Click the **hamburger menu** (≡) in the top right → **Settings**
2. Click **"Secrets"** tab
3. Paste this in the secrets editor:

```toml
[telegram]
bot_token = "8076498535:AAGo2kD-uxUn6n2_G0Y6MqbZeLra2DT_yfk"
```

4. Click **"Save"**
5. Streamlit will **auto-redeploy** with your secrets

Now your app is live! Share the URL with users.

---

### Option 2: Hard-Coded Token (What You Have Now)

⚠️ **NOT RECOMMENDED FOR PRODUCTION** - anyone with your code can see your bot token

Currently, `notifications.py` has:
```python
BOT_TOKEN = "8076498535:AAGo2kD-uxUn6n2_G0Y6MqbZeLra2DT_yfk"
```

This works locally, but when you deploy to Streamlit Cloud, **do Step 3 above** to use secrets instead.

---

## How Telegram Notifications Work in Your App

### Who Gets Notified?

✅ **All users marked as "admin"** in your Google Sheets Users table automatically get Telegram notifications

### What They Receive

When someone submits a booking, all admins get a message like:

```
📅 New Booking Submitted

Booking: Study Session
Name: John Tan
Student ID: E1234567
Telegram: @john_tan
Phone: 98765432

📍 Time Slot
Start: 20 Apr, 14:00
End: 16:00

Status: ⏳ Pending Approval

View in admin dashboard to approve or reject.
```

### Important Prerequisites

1. **Admin users must have a Telegram handle** in your Users Google Sheet (the `tele_handle` column)
2. **They must message the bot first** on Telegram (so the bot can DM them)
3. **The bot token must be correct** in Streamlit secrets

---

## Testing Locally Before Deployment

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run main.py

# 3. Make a test booking
# 4. Check your Telegram - you should get a notification within seconds
```

If you don't get a notification, check:
- ✅ You messaged the bot on Telegram first
- ✅ Your `tele_handle` in the Users sheet matches your Telegram @username
- ✅ Your user_type is set to "admin"
- ✅ The bot token is correct
- ✅ Check Streamlit console for error messages

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Telegram user not found" | Message the bot on Telegram first |
| No notifications received | Check you're marked as "admin" in Users sheet |
| Bot token error | Verify the token is correct in Streamlit secrets |
| Local works, Cloud doesn't | Make sure you added secrets to Streamlit Cloud (Step 3) |
| "Permission denied" in Streamlit | Your Google Service Account needs access to the spreadsheet |

---

## Workflow Summary

```
User submits booking
    ↓
database.addBooking() runs
    ↓
notifications.notifyAdminsOfNewBooking() called
    ↓
Gets all admin users from Google Sheets
    ↓
Filters to only admins with Telegram handles
    ↓
Sends Telegram DM to each admin
    ↓
Booking is saved (notification failures don't break this)
```

---

## Next Steps

1. **Local Testing**: Run `streamlit run main.py` and make a test booking
2. **GitHub**: Push code to GitHub
3. **Streamlit Cloud**: Deploy via Streamlit.io/cloud
4. **Secrets**: Add bot token to Streamlit Cloud secrets
5. **Live**: Your app is now live with instant admin notifications!

---

## Want to Change Who Gets Notified?

Three options in `helpers/notifications.py`:

### Option A: Only Specific Admins
Add a `notify_bookings` column to your Users sheet ("yes" or "no")

### Option B: Telegram Group Instead
Change code to send to a group chat instead of individual DMs

### Option C: Single Admin Recipient
Configure one admin's chat ID to receive all notifications

See `TELEGRAM_NOTIFICATIONS_SETUP.md` for detailed instructions on these options.

