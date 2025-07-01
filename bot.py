
import os, logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from sqlite3 import connect

BOT_TOKEN = "YOUR_BOT_TOKEN"
DB = "bot.db"

logging.basicConfig(level=logging.INFO)
conn = connect(DB)
conn.execute("CREATE TABLE IF NOT EXISTS users(uid INTEGER PRIMARY KEY, ref_count INTEGER DEFAULT 0)")
conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    args = context.args[0] if context.args else None
    if args and args.isdigit():
        conn.execute("UPDATE users SET ref_count = ref_count + 1 WHERE uid=?", (int(args),))
        conn.commit()
    conn.execute("INSERT OR IGNORE INTO users(uid) VALUES(?)", (uid,))
    conn.commit()
    msg = '''🌀 Welcome to JATT LOGGER v2.7 – Ethical Info Bot ⚙️

👑 FIRST OFFICIAL COLLAB: Mr_rack x Noval
Free Mode = 15 features | Premium Mode = 23 features (unlock after 5 referrals)
🔗 /hack – Free Logger
🔐 /advencebot – Premium Logger (after 5 referrals)

⚠️ Disclaimer: Educational use only.

Bot by Mr_rack x noval 🚀'''
    await update.message.reply_text(msg)

async def hack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = "https://yourdomain.com/f/index.html"
    await update.message.reply_text(f"✅ Free Logger Activated\n🔗 {link}\nBot by Mr_rack x noval")

async def advencebot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    row = conn.execute("SELECT ref_count FROM users WHERE uid=?", (uid,)).fetchone()
    count = row[0] if row else 0
    if count < 5:
        msg = f"🔐 Locked! You need 5 referrals to unlock.\n👥 {count}/5 done"
        await update.message.reply_text(msg)
    else:
        link = "https://yourdomain.com/p/index.html"
        await update.message.reply_text(f"👑 Premium Logger Activated\n🔗 {link}\nBot by Mr_rack x noval")

async def refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    row = conn.execute("SELECT ref_count FROM users WHERE uid=?", (uid,)).fetchone()
    count = row[0] if row else 0
    await update.message.reply_text(f"👥 Your referrals: {count}/5")

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📌 JATT LOGGER BOT v2.7\nCreated by Mr_rack x Noval\nEducational logger with Free & Premium modes."
    await update.message.reply_text(msg)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("hack", hack))
    app.add_handler(CommandHandler("advencebot", advencebot))
    app.add_handler(CommandHandler("refer", refer))
    app.add_handler(CommandHandler("about", about))
    app.run_polling()
