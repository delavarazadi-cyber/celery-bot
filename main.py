import os
import logging
import threading
import requests
from bs4 import BeautifulSoup
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

app = Flask(__name__)
@app.route('/')
def home():
    return "Berlin Free Items Agent is running!"

def run_server():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def search_kleinanzeigen():
    # محدود کردن به چند مورد اصلی برای جلوگیری از تایم‌اوت یا مسدود شدن
    items_to_search = ["Drucker", "Handy", "Kabel", "Powerbank"]
    
    found_results = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    for query in items_to_search:
        url = f"https://www.kleinanzeigen.de/s-berlin/zu-verschenken/{query}/k0c192l3331"
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                ads = soup.find_all('article', class_='aditem', limit=1) # یک مورد برتر برای هرکدام
                
                for ad in ads:
                    title_elem = ad.find('a', class_=['ellipsis', 'text-link'])
                    link_elem = ad.find('a', href=True)
                    loc_elem = ad.find('div', class_='aditem-main--top--left')
                    
                    if title_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        link = "https://www.kleinanzeigen.de" + link_elem['href']
                        location = loc_elem.get_text(strip=True) if loc_elem else "برلین"
                        
                        found_results.append(f"🔍 **{query}**\n📌 {title}\n📍 منطقه: {location}\n🔗 [لینک آگهی]({link})\n------------------")
        except Exception as e:
            logging.error(f"Error searching {query}: {e}")
            
    if not found_results:
        return "امروز مورد جدیدی پیدا نشد."
    
    return "🎁 **گزارش اقلام رایگان جدید در برلین:**\n\n" + "\n".join(found_results)

async def send_daily_report(context: ContextTypes.DEFAULT_TYPE):
    CHAT_ID = "5668005129"
    report_text = search_kleinanzeigen()
    await context.bot.send_message(chat_id=CHAT_ID, text=report_text, parse_mode="Markdown")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! ربات آماده است. برای جستجو دستور /search را بزنید.")

async def manual_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ در حال جستجو در برلین...")
    report_text = search_kleinanzeigen()
    await update.message.reply_text(report_text, parse_mode="Markdown", disable_web_page_preview=True)

if __name__ == '__main__':
    t = threading.Thread(target=run_server)
    t.start()

    TOKEN = os.environ.get('TELEGRAM_TOKEN')
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('search', manual_search))

    scheduler = BackgroundScheduler()
    scheduler.add_job(send_daily_report, 'cron', hour=9, minute=0, args=[application])
    scheduler.start()

    print("Berlin Agent is running...")
    application.run_polling()
