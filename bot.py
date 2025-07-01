import os
import json
import logging
import requests
import html
from flask import Flask, request, jsonify

# === CONFIG ===
TOKEN = "7580768387:AAFbDPp9dIm2zTYhOCXi8VHiV65Nu7P54Jg"
BOT_USERNAME = "TRACKER_R_N_bot"
API_URL = f"https://api.telegram.org/bot{TOKEN}"
DOMAIN = "https://noval-bot.onrender.com"
USER_DB = "users.json"

# === INIT ===
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Create users.json if it doesn't exist
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
    res = requests.post(f"{API_URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": html.escape(text),
        "parse_mode": "HTML"
    })
    logging.info(f"[SEND] To {chat_id} | Status: {res.status_code} | Response: {res.text}")

# === MAIN WEBHOOK ===
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json(force=True)
    logging.info(f"[WEBHOOK] Update: {json.dumps(update, indent=2)}")

    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        full_text = message.get("text", "")
        text = full_text.strip().lower()
        user_id = str(chat_id)
        username = message["from"].get("username") or f"User_{user_id}"

        users = load_users()
        if user_id not in users:
            users[user_id] = {"username": username, "referrals": 0}

        # === /start ===
        if text.startswith("/start"):
            ref_id = None
            if " " in full_text:
                try:
                    ref_id = full_text.split()[1]
                    if ref_id != user_id and ref_id in users:
                        users[ref_id]["referrals"] += 1
                        send_message(int(ref_id), f"🎉 New referral joined!\nYou now have {users[ref_id]['referrals']}/5 referrals.")
                except Exception as e:
                    logging.error(f"[ERROR] Referral logic failed: {e}")

            send_message(chat_id,
                f"👋 Welcome <b>{username}</b>\n\n"
                "🧲 Use /hack for Free Logger\n"
                "🔐 Use /advancebot for Premium Logger\n"
                "👥 Use /refer to see your referrals\n\n"
                f"🔗 Your Invite Link:\nhttps://t.me/{BOT_USERNAME}?start={user_id}"
            )

        # === /hack ===
        elif text == "/hack":
            send_message(chat_id, "🧲 <b>Free Logger Link:</b>\nhttps://yourdomain.com/f/")

        # === /advancebot ===
        elif text == "/advancebot":
            if users[user_id]["referrals"] >= 5:
                send_message(chat_id, "🔓 <b>Premium Logger Link:</b>\nhttps://yourdomain.com/p/")
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
                "<b>🤖 TRACKER_R_N_bot</b>\n"
                "👤 Made by: @rack_mr\n\n"
                "🧲 <b>Features:</b>\n"
                "• Free Logger → /hack\n"
                "• Premium Logger → /advancebot\n"
                "• Referral System → /refer\n"
                f"• Invite others: https://t.me/{BOT_USERNAME}?start=YOUR_ID"
            )

        save_users(users)

    return jsonify({"status": "ok"})

# === ROUTES ===
@app.route("/", methods=["GET"])
def home():
    return "✅ Bot is Running!"

@app.route("/setwebhook", methods=["GET"])
def setwebhook():
    url = f"{DOMAIN}/{TOKEN}"
    res = requests.get(f"{API_URL}/setWebhook", params={"url": url})
    logging.info(f"[SETWEBHOOK] Response: {res.text}")
    return res.text

# === LOCAL RUN ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
