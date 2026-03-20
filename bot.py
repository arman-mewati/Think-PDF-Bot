import telebot
import threading
from flask import Flask
from config import BOT_TOKEN

# handlers import
from handlers import pdf_tools, convert_tools, advanced_tools

bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running ✅"

def run_web():
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# register handlers
pdf_tools.register(bot)
convert_tools.register(bot)
advanced_tools.register(bot)

@bot.message_handler(commands=['start'])
def start(msg):
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

    m = InlineKeyboardMarkup()
    m.row(
        InlineKeyboardButton("📂 PDF Tools", callback_data="pdf_tools"),
        InlineKeyboardButton("🔄 Convert", callback_data="convert")
    )
    m.row(
        InlineKeyboardButton("🧰 Advanced", callback_data="advanced")
    )

    bot.send_message(msg.chat.id, "🤖 ThinkPDFBot\n\nSelect a category 👇", reply_markup=m)

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    run_bot()
