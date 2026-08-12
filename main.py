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
    return "Berlin Agent is ALIVE and RUNNING!"

def run_server():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def search_kleinanzeigen():
    # دسته‌بندی‌های ترکیبی برای جلوگیری از اشباع درخواست‌ها
    # ما از کلمات کلیدی هوشمندانه استفاده می‌کنیم
    targets = [
        ("Elektronik", "Drucker"),
        ("Lebensmittel", "Lebensmittel"),
        ("Hygiene", "Hygieneartikel")
    ]
    
    found_results = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }

    for cat_name, query in targets:
        url = f"https://www.kleinanzeigen.de/s-berlin/zu-verschenken/{query}/k0c192l3331"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # برداشتن فقط 2 مورد برتر برای هر دسته تا سبک بماند
                ads = soup.find_all('article', class_='aditem', limit=2)
                
                for ad in ads:
                    title_elem = ad.find('a', class_=['ellipsis', 'text-link'])
                    link_elem = ad.find('a', href=True)
                    if title_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        link = "https://www.kleinanzeigen.de" + link_elem['href']
                        found_results.append(f"📦 *{cat_name}*: {title}\n🔗 [لینک]({link})")
            
            # فاصله زمانی بسیار مهم برای جلوگیری از بلاک شدن IP
            time.sleep(3) 
        except Exception as e:
            logging.error(f"Error in {cat_name}: {e}")
            
    return "\n\n".join(found_results) if found_results else "مورد جدیدی یافت نشد."

async def manual_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔎 در حال جستجوی هوشمند در گروه‌های کالا و مواد غذایی...")
    report = search_kleinanzeigen()
    await update.message.reply_text(report, parse_mode="Markdown")

if __name__ == '__main__':
    threading.Thread(target=run_server).start()
    TOKEN = os.environ.get('TELEGRAM_TOKEN')
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('search', manual_search))
    
    # گزارش صبحگاهی ساعت 09:00
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: None, 'cron', hour=9, minute=0) # جایگزین برای تست
    scheduler.start()
    
    application.run_polling()
