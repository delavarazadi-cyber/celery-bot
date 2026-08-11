import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler

# تنظیمات لاگ‌گیری
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# بخش وب‌سرور برای Render
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"

def run_server():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# تابعی که قرار است هر روز گزارش را بفرستد
def send_daily_report(context):
    # در اینجا ID چت خودتان را قرار دهید که قبلاً صحبت کردیم (5668005129)
    CHAT_ID = "5668005129" 
    bot = context.bot
    # در اینجا می‌توانید متن گزارش خود را بنویسید
    bot.send_message(chat_id=CHAT_ID, text="☀️ سلام! این گزارش روزانه شماست که به صورت خودکار ارسال شد.")

# ثبت دستور start/
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! ربات شما برای ارسال گزارش‌های خودکار آماده است. 🎉")

if __name__ == '__main__':
    # روشن کردن سرور در پس‌زمینه
    t = threading.Thread(target=run_server)
    t.start()

    TOKEN = os.environ.get('TELEGRAM_TOKEN')
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))

    # تنظیم زمان‌بندی (هر روز ساعت 09:00 صبح)
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_daily_report, 'cron', hour=9, minute=0, args=[application])
    scheduler.start()

    print("Bot is starting with daily scheduler...")
    application.run_polling()
