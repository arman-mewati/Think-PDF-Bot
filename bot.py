import telebot
import os
import threading
from flask import Flask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)

# 🌐 Fake web server (Render fix)
@app.route('/')
def home():
    return "Bot is running ✅"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# 🎯 MAIN MENU
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

# 🚀 START
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🤖 Welcome to ThinkPDFBot!\n\nYour all-in-one PDF toolkit.\n\nSelect a category below 👇",
        reply_markup=main_menu()
    )

# 🔘 BUTTON HANDLER
@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    # 📂 PDF TOOLS
    if call.data == "pdf_tools":
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("📄 Merge PDFs", callback_data="merge"),
            InlineKeyboardButton("✂️ Split PDF", callback_data="split")
        )
        markup.row(
            InlineKeyboardButton("📉 Compress PDF", callback_data="compress"),
            InlineKeyboardButton("🔄 Rotate PDF", callback_data="rotate")
        )
        markup.row(
            InlineKeyboardButton("🔙 Back", callback_data="back")
        )

        bot.edit_message_text(
            "📂 PDF Tools\n\nChoose an action:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )

    # 🔄 CONVERT TOOLS
    elif call.data == "convert":
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("📄 → 📝 PDF to Word", callback_data="pdf_word"),
            InlineKeyboardButton("🖼️ → 📄 Image to PDF", callback_data="img_pdf")
        )
        markup.row(
            InlineKeyboardButton("🔙 Back", callback_data="back")
        )

        bot.edit_message_text(
            "🔄 Convert Tools\n\nSelect conversion type:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )

    # 🧰 ADVANCED TOOLS
    elif call.data == "advanced":
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("🔒 Protect PDF", callback_data="protect"),
            InlineKeyboardButton("🔓 Unlock PDF", callback_data="unlock")
        )
        markup.row(
            InlineKeyboardButton("💧 Add Watermark", callback_data="watermark")
        )
        markup.row(
            InlineKeyboardButton("🔙 Back", callback_data="back")
        )

        bot.edit_message_text(
            "🧰 Advanced Tools\n\nChoose a feature:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )

    # 🧠 UTILITY
    elif call.data == "utility":
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("📛 Rename File", callback_data="rename"),
            InlineKeyboardButton("👁 Preview File", callback_data="preview")
        )
        markup.row(
            InlineKeyboardButton("🔙 Back", callback_data="back")
        )

        bot.edit_message_text(
            "🧠 Utility Tools\n\nSelect an option:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )

    # 🔙 BACK BUTTON
    elif call.data == "back":
        bot.edit_message_text(
            "🤖 Welcome to ThinkPDFBot!\n\nYour all-in-one PDF toolkit.\n\nSelect a category below 👇",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=main_menu()
        )

    # 🚧 FEATURES (COMING SOON PLACEHOLDER)
    elif call.data in ["merge", "split", "compress", "rotate",
                       "pdf_word", "img_pdf",
                       "protect", "unlock", "watermark",
                       "rename", "preview"]:
        
        bot.answer_callback_query(call.id, "Feature coming soon 🚀")

# 🔁 RUN BOT
def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    t1 = threading.Thread(target=run_web)
    t1.start()

    run_bot()
