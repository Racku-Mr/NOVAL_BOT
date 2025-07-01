import os
import json
from flask import Flask, request
import requests

TOKEN = "7580768387:AAFbDPp9dIm2zTYhOCXi8VHiV65Nu7P54Jg"
API_URL = f"https://api.telegram.org/bot{TOKEN}"
DOMAIN = "https://noval-bot.onrender.com"

app = Flask(__name__)
USER_DB = "users.json"

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

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        user_id = str(chat_id)
        username = message["from"].get("username", "Unknown")

        users = load_users()
        if user_id not in users:
            users[user_id] = {
                "username": username,
                "referrals": 0
            }

        if text.startswith("/start"):
            if " " in text:
                ref_id = text.split()[1]
                if ref_id != user_id and ref_id in users:
                    users[ref_id]["referrals"] += 1
                    save_users(users)
                    send_message(ref_id, f"🎉 You got a new referral!\nTotal: {users[ref_id]['referrals']}/5")
            send_message(chat_id, f"👋 Welcome *{username}*\nUse /hack for Free Logger\nUse /advencebot for Premium Logger\nCheck /refer for your referrals.\n\nYour link:\nhttps://t.me/TRACKER_R_N_bot?start={user_id}")

        elif text == "/hack":
            send_message(chat_id, "🧲 *Free Logger Link:*\nhttps://yourdomain.com/f/")  # ← Replace this

        elif text == "/advencebot":
            if users[user_id]["referrals"] >= 5:
                send_message(chat_id, "🔓 *Premium Logger Link:*\nhttps://yourdomain.com/p/")  # ← Replace this
            else:
                send_message(chat_id, f"❌ You need 5 referrals to unlock Premium.\nYou have {users[user_id]['referrals']}.")

        elif text == "/refer":
            send_message(chat_id, f"👥 You have {users[user_id]['referrals']} referrals.\nYour link:\nhttps://t.me/TRACKER_R_N_bot?start={user_id}")

        elif text == "/about":
            send_message(chat_id, "🤖 *TRACKER_R_N_bot*\nMade by: @rack_mr\nFree + Premium Logger with referral unlock system.")

        save_users(users)
    return "ok"

@app.route("/", methods=["GET"])
def home():
    return "✅ Bot is Running!"

@app.route("/setwebhook", methods=["GET"])
def setwebhook():
    r = requests.get(f"{API_URL}/setWebhook?url={DOMAIN}/{TOKEN}")
    return r.text

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
