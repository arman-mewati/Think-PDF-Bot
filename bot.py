import telebot
import os
import threading
from flask import Flask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from PyPDF2 import PdfMerger

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)

# 🌐 Web server (Render fix)
@app.route('/')
def home():
    return "Bot is running ✅"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# 📦 User data store
user_data = {}

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
        "🤖 Welcome to ThinkPDFBot!\n\nYour all-in-one PDF toolkit.\n\nSelect a category 👇",
        reply_markup=main_menu()
    )

# 🔘 BUTTON HANDLER
@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    chat_id = call.message.chat.id

    # 📂 PDF TOOLS MENU
    if call.data == "pdf_tools":
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("📄 Merge PDFs", callback_data="merge"),
            InlineKeyboardButton("✂️ Split PDF", callback_data="split")
        )
        markup.row(
            InlineKeyboardButton("🔙 Back", callback_data="back")
        )

        bot.edit_message_text("📂 PDF Tools\n\nChoose an action:",
                              chat_id, call.message.message_id,
                              reply_markup=markup)

    # 🔀 MERGE MODE START
    elif call.data == "merge":
        user_data[chat_id] = {"mode": "merge", "files": []}
        bot.send_message(chat_id, "📄 Send multiple PDF files.\n\nWhen done, click /done")

    # 🔙 BACK
    elif call.data == "back":
        bot.edit_message_text(
            "🤖 Welcome to ThinkPDFBot!\n\nSelect a category 👇",
            chat_id,
            call.message.message_id,
            reply_markup=main_menu()
        )

# 📥 HANDLE FILES
@bot.message_handler(content_types=['document'])
def handle_docs(message):
    chat_id = message.chat.id

    if chat_id not in user_data or user_data[chat_id]["mode"] != "merge":
        bot.reply_to(message, "❌ Please select Merge option first")
        return

    if not message.document.file_name.endswith('.pdf'):
        bot.reply_to(message, "❌ Only PDF files allowed")
        return

    file_info = bot.get_file(message.document.file_id)
    downloaded = bot.download_file(file_info.file_path)

    file_name = f"{chat_id}_{len(user_data[chat_id]['files'])}.pdf"

    with open(file_name, 'wb') as f:
        f.write(downloaded)

    user_data[chat_id]["files"].append(file_name)

    bot.reply_to(message, f"✅ File added ({len(user_data[chat_id]['files'])})")

# 🏁 DONE COMMAND → MERGE
@bot.message_handler(commands=['done'])
def done(message):
    chat_id = message.chat.id

    if chat_id not in user_data or len(user_data[chat_id]["files"]) < 2:
        bot.reply_to(message, "❌ Send at least 2 PDF files")
        return

    bot.send_message(chat_id, "⏳ Merging PDFs...")

    merger = PdfMerger()

    for pdf in user_data[chat_id]["files"]:
        merger.append(pdf)

    output = f"{chat_id}_merged.pdf"
    merger.write(output)
    merger.close()

    with open(output, 'rb') as f:
        bot.send_document(chat_id, f)

    # 🧹 cleanup
    for file in user_data[chat_id]["files"]:
        os.remove(file)

    os.remove(output)
    user_data.pop(chat_id)

# 🔁 RUN
def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    t1 = threading.Thread(target=run_web)
    t1.start()

    run_bot()
