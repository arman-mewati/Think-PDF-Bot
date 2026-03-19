import telebot
import os
import threading
from flask import Flask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running ✅"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# 🎯 MAIN MENU (INLINE)
def main_menu():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("📂 PDF Tools", callback_data="pdf_tools"),
        InlineKeyboardButton("🔄 Convert", callback_data="convert")
    )
    markup.row(
        InlineKeyboardButton("🧰 Advanced", callback_data="advanced"),
        InlineKeyboardButton("🧠 Utility", callback_data="utility")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🤖 Welcome to ThinkPDFBot!\n\nChoose a category 👇",
        reply_markup=main_menu()
    )

# 🔘 BUTTON HANDLER
@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    if call.data == "pdf_tools":
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("📄 Merge PDF", callback_data="merge"),
            InlineKeyboardButton("✂️ Split PDF", callback_data="split")
        )
        markup.row(
            InlineKeyboardButton("📉 Compress", callback_data="compress"),
            InlineKeyboardButton("🔄 Rotate", callback_data="rotate")
        )
        markup.row(
            InlineKeyboardButton("🔙 Back", callback_data="back")
        )

        bot.edit_message_text(
            "📂 PDF Tools",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )

    elif call.data == "convert":
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("📄➡️📝 PDF to Word", callback_data="pdf_word"),
            InlineKeyboardButton("🖼️➡️📄 Image to PDF", callback_data="img_pdf")
        )
        markup.row(
            InlineKeyboardButton("🔙 Back", callback_data="back")
        )

        bot.edit_message_text(
            "🔄 Convert Tools",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )

    elif call.data == "advanced":
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("🔒 Protect PDF", callback_data="protect"),
            InlineKeyboardButton("🔓 Unlock PDF", callback_data="unlock")
        )
        markup.row(
            InlineKeyboardButton("💧 Watermark", callback_data="watermark")
        )
        markup.row(
            InlineKeyboardButton("🔙 Back", callback_data="back")
        )

        bot.edit_message_text(
            "🧰 Advanced Tools",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )

    elif call.data == "utility":
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("📛 Rename", callback_data="rename"),
            InlineKeyboardButton("👁 Preview", callback_data="preview")
        )
        markup.row(
            InlineKeyboardButton("🔙 Back", callback_data="back")
        )

        bot.edit_message_text(
            "🧠 Utility Tools",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )

    elif call.data == "back":
        bot.edit_message_text(
            "🤖 Welcome to ThinkPDFBot!\n\nChoose a category 👇",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=main_menu()
        )

# 🔁 Run
def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    t1 = threading.Thread(target=run_web)
    t1.start()

    run_bot()
