import os
import logging
import threading
import requests
from bs4 import BeautifulSoup
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_server():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def search_kleinanzeigen():
    targets = [
        ("مواد غذایی", "charlottenburg/Lebensmittel"),
        ("بهداشتی", "mitte/Hygieneartikel"),
        ("لوازم ماشین", "wilmersdorf/Auto+Ladegerät"),
        ("الکترونیک", "berlin/Drucker")
    ]
    
    found_results = []
    seen_links = set()  # جلوگیری از لینک‌های تکراری در یک جستجو
    headers = {"User-Agent": "Mozilla/5.0"}

    for cat_name, path in targets:
        url = f"https://www.kleinanzeigen.de/s-c{path}/zu-verschenken/k0c192l3331"
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                ads = soup.find_all('article', class_='aditem', limit=1)
                for ad in ads:
                    link_tag = ad.find('a', href=True)
                    if link_tag:
                        link = "https://www.kleinanzeigen.de" + link_tag['href']
                        if link not in seen_links:
                            seen_links.add(link)
                            title = ad.find('a', class_=['ellipsis', 'text-link']).get_text(strip=True)
                            found_results.append(f"📦 *{cat_name}*: {title}\n🔗 [لینک]({link})")
        except: continue
            
    return "\n\n".join(found_results) if found_results else None

# تابع ارسال خودکار گزارش ساعت ۹ صبح
async def auto_report(application):
    chat_id = os.environ.get('TELEGRAM_CHAT_ID') # چت آیدی از متغیرهای محیطی خوانده می‌شود
    if chat_id:
        report = search_kleinanzeigen()
        if report:
            await application.bot.send_message(chat_id=chat_id, text=f"☀️ گزارش خودکار صبحگاهی:\n\n{report}", parse_mode="Markdown")

async def manual_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔎 در حال جستجوی هوشمند و بدون تکرار...")
    report = search_kleinanzeigen()
    if report:
        await update.message.reply_text(report, parse_mode="Markdown")
    else:
        await update.message.reply_text("مورد جدیدی یافت نشد.")

if __name__ == '__main__':
    threading.Thread(target=run_server).start()
    TOKEN = os.environ.get('TELEGRAM_TOKEN')
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('search', manual_search))
    
    # تنظیم زمان‌بندی برای ساعت ۹ صبح هر روز
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: application.create_task(auto_report(application)), 'cron', hour=9, minute=0)
    scheduler.start()
    
    application.run_polling()
