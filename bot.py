import telebot
import os
from telebot.types import ReplyKeyboardMarkup

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

user_files = {}

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📂 PDF Tools", "🔄 Convert Tools")
    markup.add("🧰 Advanced", "🧠 Utility")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🤖 Welcome to ThinkPDFBot!", reply_markup=main_menu())

@bot.message_handler(func=lambda msg: True)
def handle_menu(message):
    if message.text == "📂 PDF Tools":
        bot.send_message(message.chat.id, "Send multiple PDFs then type /merge")

    elif message.text == "🔄 Convert Tools":
        bot.send_message(message.chat.id, "Send PDF to convert to Word")

    elif message.text == "🧰 Advanced":
        bot.send_message(message.chat.id, "Advanced tools coming soon 🚀")

    elif message.text == "🧠 Utility":
        bot.send_message(message.chat.id, "Utility tools coming soon ⚙️")

bot.polling()
