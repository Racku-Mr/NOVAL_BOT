import os
import json
import logging
import requests
from flask import Flask, request, jsonify

# --- CONFIG ---
TOKEN = os.getenv("TOKEN", "YOUR_TOKEN_HERE")
BOT_USERNAME = os.getenv("BOT_USERNAME", "YourBot")
API_URL = f"https://api.telegram.org/bot{TOKEN}"
DOMAIN = os.getenv("DOMAIN", "https://your-domain.com")
USER_DB = "users.json"

# --- INIT ---
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    r = requests.post(f"{API_URL}/sendMessage", json=payload)
    logger.info(f"Sent message to {chat_id}: {r.status_code}, {r.text}")

# === WEBHOOK ENDPOINT ===
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json(force=True)
    logger.info("Update received: %s", update)

    if "message" in update:
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        user_id = str(chat_id)
        full_text = msg.get("text", "")
        text = full_text.strip().lower()
        username = msg["from"].get("username") or msg["from"].get("first_name", "")

        users = load_users()
        if user_id not in users:
            users[user_id] = {"username": username, "referrals": 0}

        if text.startswith("/start"):
            # handle optional referral
            parts = full_text.split()
            if len(parts) > 1:
                ref_id = parts[1]
                if ref_id != user_id and ref_id in users:
                    users[ref_id]["referrals"] += 1
                    send_message(int(ref_id),
                                 f"🎉 You got a referral! Total: {users[ref_id]['referrals']}/5")
            send_message(chat_id,
                         f"👋 Welcome, *{username}*!\n\n"
                         "🧲 Use /hack for Free Logger\n"
                         "🔐 Use /advancebot for Premium Logger\n"
                         "👥 Use /refer to check referrals\n\n"
                         f"🔗 Invite: https://t.me/{BOT_USERNAME}?start={user_id}")

        elif text == "/hack":
            send_message(chat_id, "🧲 *Free Logger Link:*\nhttps://yourdomain.com/f/")

        elif text == "/advancebot":
            if users[user_id]["referrals"] >= 5:
                send_message(chat_id, "🔓 *Premium Logger Link:*\nhttps://yourdomain.com/p/")
            else:
                send_message(chat_id,
                             f"❌ Need 5 referrals. You have {users[user_id]['referrals']}.")

        elif text == "/refer":
            send_message(chat_id,
                         f"👥 You have {users[user_id]['referrals']} referrals.\n\n"
                         f"🔗 Invite link: https://t.me/{BOT_USERNAME}?start={user_id}")

        elif text == "/about":
            send_message(chat_id,
                         "🤖 *TRACKER_BOT*\n"
                         "👤 Made by: @rack_mr\n\n"
                         "🧲 Features:\n"
                         "• Free Logger → /hack\n"
                         "• Premium Logger → /advancebot\n"
                         "• Referral System → /refer")

        save_users(users)

    return jsonify({"status": "ok"})


@app.route("/setwebhook", methods=["GET"])
def setwebhook():
    url = f"{DOMAIN}/{TOKEN}"
    r = requests.get(f"{API_URL}/setWebhook", params={"url": url})
    logger.info("SetWebhook response: %s", r.text)
    return r.text


@app.route("/", methods=["GET"])
def home():
    return "✅ Bot alive!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
