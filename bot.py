import telebot
import os
import threading
from flask import Flask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from PyPDF2 import PdfMerger
from pdf2docx import Converter
import img2pdf

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running ✅"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

user_data = {}

# 🎯 MAIN MENU
def main_menu():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("📂 PDF Tools", callback_data="pdf_tools"),
        InlineKeyboardButton("🔄 Convert", callback_data="convert")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🤖 Welcome to ThinkPDFBot!\n\nSelect a category 👇",
        reply_markup=main_menu()
    )

# 🔘 BUTTON HANDLER
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id

    if call.data == "pdf_tools":
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("📄 Merge PDFs", callback_data="merge")
        )
        markup.row(
            InlineKeyboardButton("🔙 Back", callback_data="back")
        )

        bot.edit_message_text("📂 PDF Tools", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data == "convert":
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("📄 → 📝 PDF to Word", callback_data="pdf_word")
        )
        markup.row(
            InlineKeyboardButton("🖼️ → 📄 Image to PDF", callback_data="img_pdf")
        )
        markup.row(
            InlineKeyboardButton("🔙 Back", callback_data="back")
        )

        bot.edit_message_text("🔄 Convert Tools", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data == "merge":
        user_data[chat_id] = {"mode": "merge", "files": []}
        bot.send_message(chat_id, "📄 Send multiple PDFs then type /done")

    elif call.data == "pdf_word":
        user_data[chat_id] = {"mode": "pdf_word"}
        bot.send_message(chat_id, "📄 Send a PDF file")

    elif call.data == "img_pdf":
        user_data[chat_id] = {"mode": "img_pdf", "files": []}
        bot.send_message(chat_id, "🖼️ Send images (JPG/PNG) then type /done")

    elif call.data == "back":
        bot.edit_message_text(
            "🤖 Welcome to ThinkPDFBot!\n\nSelect a category 👇",
            chat_id,
            call.message.message_id,
            reply_markup=main_menu()
        )

# 📥 HANDLE FILES
@bot.message_handler(content_types=['document', 'photo'])
def handle_files(message):
    chat_id = message.chat.id

    if chat_id not in user_data:
        bot.reply_to(message, "❌ Choose a tool first")
        return

    mode = user_data[chat_id]["mode"]

    # 🔀 MERGE
    if mode == "merge":
        if not message.document or not message.document.file_name.endswith('.pdf'):
            bot.reply_to(message, "❌ Send PDF files only")
            return

        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)

        file_name = f"{chat_id}_{len(user_data[chat_id]['files'])}.pdf"

        with open(file_name, 'wb') as f:
            f.write(downloaded)

        user_data[chat_id]["files"].append(file_name)
        bot.reply_to(message, f"✅ Added ({len(user_data[chat_id]['files'])})")

    # 🔄 PDF → WORD
    elif mode == "pdf_word":
        if not message.document or not message.document.file_name.endswith('.pdf'):
            bot.reply_to(message, "❌ Send PDF only")
            return

        bot.send_message(chat_id, "⏳ Converting...")

        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)

        input_file = f"{chat_id}.pdf"
        output_file = f"{chat_id}.docx"

        with open(input_file, 'wb') as f:
            f.write(downloaded)

        cv = Converter(input_file)
        cv.convert(output_file)
        cv.close()

        with open(output_file, 'rb') as f:
            bot.send_document(chat_id, f)

        os.remove(input_file)
        os.remove(output_file)
        user_data.pop(chat_id)

    # 🖼️ IMAGE → PDF
    elif mode == "img_pdf":
        file_id = None

        if message.photo:
            file_id = message.photo[-1].file_id
        elif message.document:
            file_id = message.document.file_id

        file_info = bot.get_file(file_id)
        downloaded = bot.download_file(file_info.file_path)

        file_name = f"{chat_id}_{len(user_data[chat_id]['files'])}.jpg"

        with open(file_name, 'wb') as f:
            f.write(downloaded)

        user_data[chat_id]["files"].append(file_name)
        bot.reply_to(message, f"✅ Image added ({len(user_data[chat_id]['files'])})")

# 🏁 DONE COMMAND
@bot.message_handler(commands=['done'])
def done(message):
    chat_id = message.chat.id

    if chat_id not in user_data:
        return

    mode = user_data[chat_id]["mode"]

    # MERGE
    if mode == "merge":
        if len(user_data[chat_id]["files"]) < 2:
            bot.reply_to(message, "❌ Send at least 2 PDFs")
            return

        bot.send_message(chat_id, "⏳ Merging...")

        merger = PdfMerger()
        for pdf in user_data[chat_id]["files"]:
            merger.append(pdf)

        output = f"{chat_id}_merged.pdf"
        merger.write(output)
        merger.close()

        with open(output, 'rb') as f:
            bot.send_document(chat_id, f)

    # IMAGE → PDF
    elif mode == "img_pdf":
        if len(user_data[chat_id]["files"]) < 1:
            bot.reply_to(message, "❌ Send at least 1 image")
            return

        bot.send_message(chat_id, "⏳ Creating PDF...")

        output = f"{chat_id}_images.pdf"

        with open(output, "wb") as f:
            f.write(img2pdf.convert(user_data[chat_id]["files"]))

        with open(output, 'rb') as f:
            bot.send_document(chat_id, f)

    # CLEANUP
    for file in user_data[chat_id]["files"]:
        os.remove(file)

    if os.path.exists(output):
        os.remove(output)

    user_data.pop(chat_id)

# 🔁 RUN
def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    t1 = threading.Thread(target=run_web)
    t1.start()

    run_bot()
