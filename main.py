import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# تنظیمات لاگ‌گیری
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# بخش وب‌سرور برای Render
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"

def run_server():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# پاسخ به دستور start/
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من ربات شما هستم و کاملاً آماده کارم. 🎉")

# پاسخ به هر پیام متنی ساده (تست مکالمه)
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text(f"شما گفتید: {user_text} - من صدایتان را می‌شنوم!")

if __name__ == '__main__':
    t = threading.Thread(target=run_server)
    t.start()

    TOKEN = os.environ.get('TELEGRAM_TOKEN')
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    # اضافه کردن بخش پاسخ به پیام‌های متنی
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))

    print("Bot is ready and listening...")
    application.run_polling()
