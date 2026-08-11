import os
from flask import Flask
from threading import Thread
import time

# بخش وب سرور برای اینکه Render راضی بماند
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"

def run_server():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# شروع اجرای ربات اصلی شما
def run_bot():
    # اینجا کد اصلی ربات خودتان را قرار دهید
    # مثلا: from my_bot import main; main()
    print("Bot is starting...")
    while True:
        time.sleep(60)

if __name__ == "__main__":
    Thread(target=run_server).start()
    run_bot()
