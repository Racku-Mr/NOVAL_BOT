import os
import json
from flask import Flask, request
import requests

# === CONFIG ===
TOKEN = "7580768387:AAFbDPp9dIm2zTYhOCXi8VHiV65Nu7P54Jg"
BOT_USERNAME = "TRACKER_R_N_bot"
API_URL = f"https://api.telegram.org/bot{TOKEN}"
DOMAIN = "https://noval-bot.onrender.com"  # change to your render domain
USER_DB = "users.json"

# === APP INIT ===
app = Flask(__name__)

if not os.path.exists(USER_DB):
    with open(USER_DB, "w") as f:
        json.dump({}, f)

def load_users():
    with open(USER_DB) as f:
        return json.load(f)

def save_users(users):
    with open(USER_DB, "w") as f:
        json.dump(users, f, indent=2)

def send_message(chat_id, text):
    requests.post(f"{API_URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    })

# === MAIN WEBHOOK ===
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        full_text = message.get("text", "")
        text = full_text.split()[0].lower()
        user_id = str(chat_id)
        username = message["from"].get("username", "Unknown")

        users = load_users()

        # initialize user if not exists
        if user_id not in users:
            users[user_id] = {"username": username, "referrals": 0}

        # === /start with referral logic ===
        if text == "/start":
            ref_id = None
            if " " in full_text:
                try:
                    ref_id = full_text.split()[1]
                except:
                    ref_id = None

            if ref_id and ref_id != user_id and ref_id in users:
                users[ref_id]["referrals"] += 1
                send_message(ref_id, f"🎉 New referral joined!\nYou now have {users[ref_id]['referrals']}/5 referrals.")

            send_message(chat_id,
                f"👋 Welcome *{username}*\n\n"
                "🧲 Use /hack for Free Logger\n"
                "🔐 Use /advancebot for Premium Logger\n"
                "👥 Use /refer to see your referrals\n\n"
                f"🔗 Your Invite Link:\nhttps://t.me/{BOT_USERNAME}?start={user_id}"
            )

        # === /hack ===
        elif text == "/hack":
            send_message(chat_id, "🧲 *Free Logger Link:*\nhttps://yourdomain.com/f/")

        # === /advancebot ===
        elif text == "/advancebot":
            if users[user_id]["referrals"] >= 5:
                send_message(chat_id, "🔓 *Premium Logger Link:*\nhttps://yourdomain.com/p/")
            else:
                send_message(chat_id, f"❌ You need 5 referrals to unlock Premium.\nYou have {users[user_id]['referrals']}.")

        # === /refer ===
        elif text == "/refer":
            send_message(chat_id,
                f"👥 You have {users[user_id]['referrals']} referrals.\n\n"
                f"🔗 Your Invite Link:\nhttps://t.me/{BOT_USERNAME}?start={user_id}"
            )

        # === /about ===
        elif text == "/about":
            send_message(chat_id,
                "🤖 *TRACKER_R_N_bot*\n"
                "👤 Made by: @rack_mr\n\n"
                "🧲 *Features:*\n"
                "• Free Logger → /hack\n"
                "• Premium Logger → /advancebot\n"
                "• Referral System → /refer\n"
                f"• Invite others: https://t.me/{BOT_USERNAME}?start=YOUR_ID"
            )

        save_users(users)

    return "ok"

# === ROUTES ===
@app.route("/", methods=["GET"])
def home():
    return "✅ Bot is Running!"

@app.route("/setwebhook", methods=["GET"])
def setwebhook():
    r = requests.get(f"{API_URL}/setWebhook?url={DOMAIN}/{TOKEN}")
    return r.text

# === RUN LOCAL ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
