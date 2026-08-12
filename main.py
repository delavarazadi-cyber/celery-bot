
import os
import logging
import threading
import requests
import time
from bs4 import BeautifulSoup
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is alive!"

def run_server():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def search_kleinanzeigen():
    # تمرکز روی محله‌های نزدیک: شارلوتن‌بورگ، میته و ویلمرزدورف
    # کدهای پستی یا نام محله‌ها در لینک Kleinanzeigen اعمال می‌شوند
    targets = [
        ("مواد غذایی (شارلوتن‌بورگ/میته)", "charlottenburg/Lebensmittel"),
        ("بهداشتی (نزدیک شما)", "mitte/Hygieneartikel"),
        ("لوازم ماشین (ویلمرزدورف)", "wilmersdorf/Auto+Ladegerät"),
        ("الکترونیک (برلین)", "berlin/Drucker")
    ]
    
    found_results = []
    headers = {"User-Agent": "Mozilla/5.0"}

    for cat_name, path in targets:
        # جستجو بر اساس محله‌های مشخص شده در برلین
        url = f"https://www.kleinanzeigen.de/s-c{path}/zu-verschenken/k0c192l3331"
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                ads = soup.find_all('article', class_='aditem', limit=1)
                for ad in ads:
                    title = ad.find('a', class_=['ellipsis', 'text-link']).get_text(strip=True)
                    link = "https://www.kleinanzeigen.de" + ad.find('a', href=True)['href']
                    found_results.append(f"📦 *{cat_name}*: {title}\n🔗 [لینک]({link})")
        except: continue
            
    return "\n\n".join(found_results) if found_results else "مورد جدیدی در این محله‌ها یافت نشد."

async def manual_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔎 جستجو در محله‌های نزدیک (شارلوتن‌بورگ، میته، ویلمرزدورف)...")
    report = search_kleinanzeigen()
    await update.message.reply_text(report, parse_mode="Markdown")

if __name__ == '__main__':
    threading.Thread(target=run_server).start()
    TOKEN = os.environ.get('TELEGRAM_TOKEN')
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('search', manual_search))
    application.run_polling()
