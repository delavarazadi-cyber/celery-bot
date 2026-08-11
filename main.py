import os
import logging
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# تنظیمات لاگ‌گیری برای نمایش خطاها
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# بخش وب‌سرور فلاسک برای راضی نگه داشتن Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_server():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# تابع پاسخ به دستور /start در تلگرام
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! ربات شما با موفقیت روشن شد و آماده به کار است. 🎉")

if __name__ == '__main__':
    import threading
    # روشن کردن سرور فلاسک در پس‌زمینه
    t = threading.Thread(target=run_server)
    t.start()

    # دریافت توکن از متغیرهای محیطی Render
    TOKEN = os.environ.get('TELEGRAM_TOKEN')
    
    # راه‌اندازی ربات با کتابخانه python-telegram-bot
    application = ApplicationBuilder().token(TOKEN).build()
    
    # ثبت دستور start/
    application.add_handler(CommandHandler('start', start))
    
    # شروع به کار ربات
    print("Bot is starting...")
    application.run_polling()
