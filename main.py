import os
import telebot
from flask import Flask

# دریافت توکن از متغیرهای محیطی Render
TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

# بخش وب‌سرور برای راضی نگه داشتن Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# پاسخ به دستور /start در تلگرام
@bot.message_handler(commands=['start'])
def send_welcome(bot_message):
    bot.reply_to(bot_message, "سلام! ربات شما با موفقیت روشن شد و آماده به کار است. 🎉")

# اجرای وب‌سرور روی یک ترد جداگانه
def run_server():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

if __name__ == "__main__":
    import threading
    # روشن کردن سرور فلاسک در پس‌زمینه
    t = threading.Thread(target=run_server)
    t.start()
    
    # شروع به کار ربات تلگرام
    print("Bot is polling...")
    bot.infinity_polling()
