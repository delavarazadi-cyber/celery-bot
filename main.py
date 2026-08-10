import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from apscheduler.schedulers.blocking import BlockingScheduler

# توکن ربات و آیدی چت شما (که بعداً از تلگرام می‌گیرید)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "TOKEN_BOT_HERE")
CHAT_ID = os.environ.get("CHAT_ID", "YOUR_CHAT_ID_HERE")

def check_and_send():
    try:
        # اینجا می‌توانید آدرس سایت مورد نظر خود برای جستجو را قرار دهید
        url = "https://example.com"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # نمونه جستجو (می‌توانید بر اساس نیاز خود تغییر دهید)
        title = soup.find('h1').text if soup.find('h1') else "نتیجه‌ای یافت شد"
        
        message = f"گزارش روزانه ربات:\n\nموضوع بررسی شده: {title}"
        
        # ارسال پیام به تلگرام
        bot = Bot(token=TELEGRAM_TOKEN)
        bot.send_message(chat_id=CHAT_ID, text=message)
        print("گزارش با موفقیت ارسال شد.")
    except Exception as e:
        print(f"خطا در ارسال گزارش: {e}")

if __name__ == "__main__":
    # تنظیم زمان‌بندی برای اجرا (مثلاً هر روز یکبار)
    scheduler = BlockingScheduler()
    scheduler.add_job(check_and_send, 'interval', days=1)
    
    # برای تست اولیه، یکبار هم هنگام شروع اجرا شود
    check_and_send()
    
    scheduler.start()
