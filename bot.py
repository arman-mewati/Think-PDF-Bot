import telebot
import os
import threading
from flask import Flask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from PyPDF2 import PdfMerger
from pdf2docx import Converter
import img2pdf
import pikepdf

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
    markup.row(
        InlineKeyboardButton("🧰 Advanced", callback_data="advanced")
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

    # PDF TOOLS
    if call.data == "pdf_tools":
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("📄 Merge PDFs", callback_data="merge")
        )
        markup.row(
            InlineKeyboardButton("🔙 Back", callback_data="back")
        )

        bot.edit_message_text("📂 PDF Tools", chat_id, call.message.message_id, reply_markup=markup)

    # CONVERT
    elif call.data == "convert":
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("📄 → 📝 PDF to Word", callback_data="pdf_word"),
            InlineKeyboardButton("🖼️ → 📄 Image to PDF", callback_data="img_pdf")
        )
        markup.row(
            InlineKeyboardButton("🔙 Back", callback_data="back")
        )

        bot.edit_message_text("🔄 Convert Tools", chat_id, call.message.message_id, reply_markup=markup)

    # ADVANCED
    elif call.data == "advanced":
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("🔒 Protect PDF", callback_data="protect"),
            InlineKeyboardButton("🔓 Unlock PDF", callback_data="unlock")
        )
        markup.row(
            InlineKeyboardButton("🔙 Back", callback_data="back")
        )

        bot.edit_message_text("🧰 Advanced Tools", chat_id, call.message.message_id, reply_markup=markup)

    # MODES
    elif call.data == "merge":
        user_data[chat_id] = {"mode": "merge", "files": []}
        bot.send_message(chat_id, "📄 Send PDFs then /done")

    elif call.data == "pdf_word":
        user_data[chat_id] = {"mode": "pdf_word"}
        bot.send_message(chat_id, "📄 Send a PDF")

    elif call.data == "img_pdf":
        user_data[chat_id] = {"mode": "img_pdf", "files": []}
        bot.send_message(chat_id, "🖼️ Send images then /done")

    elif call.data == "protect":
        user_data[chat_id] = {"mode": "protect"}
        bot.send_message(chat_id, "📄 Send PDF to protect")

    elif call.data == "unlock":
        user_data[chat_id] = {"mode": "unlock"}
        bot.send_message(chat_id, "📄 Send locked PDF")

    elif call.data == "back":
        bot.edit_message_text(
            "🤖 Welcome to ThinkPDFBot!\n\nSelect a category 👇",
            chat_id,
            call.message.message_id,
            reply_markup=main_menu()
        )

# 📥 FILE HANDLER
@bot.message_handler(content_types=['document', 'photo'])
def handle_files(message):
    chat_id = message.chat.id

    if chat_id not in user_data:
        bot.reply_to(message, "❌ Select tool first")
        return

    mode = user_data[chat_id]["mode"]

    # MERGE
    if mode == "merge":
        if not message.document or not message.document.file_name.endswith('.pdf'):
            return bot.reply_to(message, "❌ PDF only")

        file_info = bot.get_file(message.document.file_id)
        data = bot.download_file(file_info.file_path)

        name = f"{chat_id}_{len(user_data[chat_id]['files'])}.pdf"
        open(name, 'wb').write(data)

        user_data[chat_id]["files"].append(name)
        bot.reply_to(message, "✅ Added")

    # PDF → WORD
    elif mode == "pdf_word":
        file_info = bot.get_file(message.document.file_id)
        data = bot.download_file(file_info.file_path)

        open(f"{chat_id}.pdf", 'wb').write(data)

        bot.send_message(chat_id, "⏳ Converting...")

        cv = Converter(f"{chat_id}.pdf")
        cv.convert(f"{chat_id}.docx")
        cv.close()

        bot.send_document(chat_id, open(f"{chat_id}.docx", 'rb'))

        os.remove(f"{chat_id}.pdf")
        os.remove(f"{chat_id}.docx")
        user_data.pop(chat_id)

    # IMAGE → PDF
    elif mode == "img_pdf":
        file_id = message.photo[-1].file_id if message.photo else message.document.file_id
        file_info = bot.get_file(file_id)
        data = bot.download_file(file_info.file_path)

        name = f"{chat_id}_{len(user_data[chat_id]['files'])}.jpg"
        open(name, 'wb').write(data)

        user_data[chat_id]["files"].append(name)
        bot.reply_to(message, "✅ Image added")

    # PROTECT PDF
    elif mode == "protect":
        file_info = bot.get_file(message.document.file_id)
        data = bot.download_file(file_info.file_path)

        open(f"{chat_id}.pdf", 'wb').write(data)

        user_data[chat_id] = {"mode": "set_password"}
        bot.send_message(chat_id, "🔑 Send password to lock PDF")

    # UNLOCK PDF
    elif mode == "unlock":
        file_info = bot.get_file(message.document.file_id)
        data = bot.download_file(file_info.file_path)

        open(f"{chat_id}.pdf", 'wb').write(data)

        user_data[chat_id] = {"mode": "unlock_pass"}
        bot.send_message(chat_id, "🔑 Send password to unlock")

# 🔑 TEXT HANDLER (PASSWORD)
@bot.message_handler(func=lambda m: True)
def text_handler(message):
    chat_id = message.chat.id

    if chat_id not in user_data:
        return

    mode = user_data[chat_id]["mode"]

    # SET PASSWORD
    if mode == "set_password":
        password = message.text

        pdf = pikepdf.open(f"{chat_id}.pdf")
        pdf.save(f"{chat_id}_locked.pdf", encryption=pikepdf.Encryption(owner=password, user=password))
        pdf.close()

        bot.send_document(chat_id, open(f"{chat_id}_locked.pdf", 'rb'))

        os.remove(f"{chat_id}.pdf")
        os.remove(f"{chat_id}_locked.pdf")
        user_data.pop(chat_id)

    # UNLOCK PDF
    elif mode == "unlock_pass":
        password = message.text

        try:
            pdf = pikepdf.open(f"{chat_id}.pdf", password=password)
            pdf.save(f"{chat_id}_unlocked.pdf")
            pdf.close()

            bot.send_document(chat_id, open(f"{chat_id}_unlocked.pdf", 'rb'))

            os.remove(f"{chat_id}.pdf")
            os.remove(f"{chat_id}_unlocked.pdf")
            user_data.pop(chat_id)

        except:
            bot.send_message(chat_id, "❌ Wrong password")

# 🏁 DONE
@bot.message_handler(commands=['done'])
def done(message):
    chat_id = message.chat.id

    if chat_id not in user_data:
        return

    mode = user_data[chat_id]["mode"]

    if mode == "merge":
        merger = PdfMerger()
        for pdf in user_data[chat_id]["files"]:
            merger.append(pdf)

        output = f"{chat_id}_merged.pdf"
        merger.write(output)
        merger.close()

        bot.send_document(chat_id, open(output, 'rb'))

    elif mode == "img_pdf":
        output = f"{chat_id}_images.pdf"
        with open(output, "wb") as f:
            f.write(img2pdf.convert(user_data[chat_id]["files"]))

        bot.send_document(chat_id, open(output, 'rb'))

    # CLEANUP
    for f in user_data[chat_id]["files"]:
        os.remove(f)

    os.remove(output)
    user_data.pop(chat_id)

# RUN
def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    run_bot()
