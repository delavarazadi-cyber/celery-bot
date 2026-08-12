import os
import logging
import threading
import requests
import time
from bs4 import BeautifulSoup
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

app = Flask(__name__)
@app.route('/')
def home():
    return "Berlin Agent is ALIVE!"

def run_server():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def search_kleinanzeigen():
    # لیست کامل‌تر اقلام مورد نظر شما
    categories = ["Drucker", "Handy", "Kabel", "Powerbank", "Lebensmittel", "Hygieneartikel"]
    found_results = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    for query in categories:
        # جستجو در بخش رایگان برلین
        url = f"https://www.kleinanzeigen.de/s-berlin/zu-verschenken/{query}/k0c192l3331"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # فقط اولین آگهی از هر دسته را بردار تا ربات قفل نکند
                ad = soup.find('article', class_='aditem')
                
                if ad:
                    title_elem = ad.find('a', class_=['ellipsis', 'text-link'])
                    link_elem = ad.find('a', href=True)
                    if title_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        link = "https://www.kleinanzeigen.de" + link_elem['href']
                        found_results.append(f"📦 *{query}*: {title}\n🔗 [لینک]({link})")
            
            # تاخیر کوتاه برای جلوگیری از مسدود شدن IP توسط سایت
            time.sleep(2) 
        except Exception as e:
            logging.error(f"Error: {e}")
            
    return "\n\n".join(found_results) if found_results else "مورد جدیدی یافت نشد."

async def send_daily_report(context: ContextTypes.DEFAULT_TYPE):
    report = search_kleinanzeigen()
    await context.bot.send_message(chat_id="5668005129", text=f"☀️ *گزارش صبحگاهی:* \n\n{report}", parse_mode="Markdown")

async def manual_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔎 در حال جستجوی هوشمند...")
    report = search_kleinanzeigen()
    await update.message.reply_text(report, parse_mode="Markdown")

if __name__ == '__main__':
    threading.Thread(target=run_server).start()
    TOKEN = os.environ.get('TELEGRAM_TOKEN')
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('search', manual_search))
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_daily_report, 'cron', hour=9, minute=0)
    scheduler.start()
    
    application.run_polling()
