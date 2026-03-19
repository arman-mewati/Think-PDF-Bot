import telebot
import os
import threading
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# 🔥 Flask app (fake web server for Render)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running ✅"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# 🤖 Bot code
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🤖 Welcome to ThinkPDFBot!")

def run_bot():
    bot.infinity_polling()

# 🔁 Run both together
if __name__ == "__main__":
    t1 = threading.Thread(target=run_web)
    t1.start()
    
    run_bot()
