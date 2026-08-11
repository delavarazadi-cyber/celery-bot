import os
import logging
import threading
import requests
from bs4 import BeautifulSoup
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler

# تنظیمات لاگ‌گیری
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# وب‌سرور برای زنده نگه داشتن ربات در Render
app = Flask(__name__)
@app.route('/')
def home():
    return "Berlin Free Items Agent is running!"

def run_server():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# لیست کارهایی که باید در Kleinanzeigen جستجو شوند (بخش Zu verschenken در برلین)
# لینک پایه برای جستجوی اقلام رایگان در برلین
def search_kleinanzeigen():
    items_to_search = [
        "Drucker", "Handy", "Kabel", "USB", "Maus", 
        "Tastatur", "SD Card", "Powerbank", "Schreibwaren", 
        "Künstliche Blumen", "Lebensmittel", "Hygieneartikel"
    ]
    
    found_results = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for query in items_to_search:
        # ساخت لینک جستجو در بخش Zu verschenken برلین
        url = f"https://www.kleinanzeigen.de/s-berlin/zu-verschenken/{query}/k0c192l3331"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # پیدا کردن آگهی‌ها در صفحه
                ads = soup.find_all('article', class_='aditem', limit=2) # حداکثر 2 مورد برای هر آیتم که پیام‌ها شلوغ نشود
                
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
        return "امروز مورد جدیدی با لیست شما در بخش رایگان برلین پیدا نشد."
    
    return "🎁 **گزارش اقلام رایگان جدید در برلین (Kleinanzeigen):**\n\n" + "\n".join(found_results[:8]) # ارسال حداکثر ۸ مورد برتر

# تابع ارسال خودکار گزارش
async def send_daily_report(context: ContextTypes.DEFAULT_TYPE):
    CHAT_ID = "5668005129" # آیدی چت شما
    report_text = search_kleinanzeigen()
    await context.bot.send_message(chat_id=CHAT_ID, text=report_text, parse_mode="Markdown")

# دستور استارت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! ایجنت هوشمند برلین آماده است. من سایت Kleinanzeigen را برای اقلام رایگان رصد می‌کنم. برای دریافت دستی گزارش، دستور /search را بفرستید.")

# دستور جستجوی دستی برای تست فوری
async def manual_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ در حال جستجوی اقلام رایگان در برلین...")
    report_text = search_kleinanzeigen()
    await update.message.reply_text(report_text, parse_mode="Markdown", disable_web_page_preview=True)

if __name__ == '__main__':
    t = threading.Thread(target=run_server)
    t.start()

    TOKEN = os.environ.get('TELEGRAM_TOKEN')
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('search', manual_search))

    # تنظیم زمان‌بندی برای اجرای خودکار هر روز ساعت ۰۹:۰۰ صبح
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_daily_report, 'cron', hour=9, minute=0, args=[application])
    scheduler.start()

    print("Berlin Agent is running...")
    application.run_polling()
