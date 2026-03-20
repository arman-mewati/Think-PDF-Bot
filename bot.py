import telebot
import os
import threading
from flask import Flask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
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

# 🎯 MENU
def main_menu():
    m = InlineKeyboardMarkup()
    m.row(InlineKeyboardButton("📂 PDF Tools", callback_data="pdf_tools"),
          InlineKeyboardButton("🔄 Convert", callback_data="convert"))
    m.row(InlineKeyboardButton("🧰 Advanced", callback_data="advanced"))
    return m

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id,
                     "🤖 ThinkPDFBot\n\nAll-in-one PDF toolkit",
                     reply_markup=main_menu())

# 🔘 BUTTONS
@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    cid = call.message.chat.id

    if call.data == "pdf_tools":
        m = InlineKeyboardMarkup()
        m.row(InlineKeyboardButton("📄 Merge", callback_data="merge"))
        m.row(InlineKeyboardButton("📉 Compress", callback_data="compress"))
        m.row(InlineKeyboardButton("🔙 Back", callback_data="back"))
        bot.edit_message_text("PDF Tools", cid, call.message.message_id, reply_markup=m)

    elif call.data == "convert":
        m = InlineKeyboardMarkup()
        m.row(InlineKeyboardButton("PDF → Word", callback_data="pdf_word"))
        m.row(InlineKeyboardButton("Image → PDF", callback_data="img_pdf"))
        m.row(InlineKeyboardButton("🔙 Back", callback_data="back"))
        bot.edit_message_text("Convert", cid, call.message.message_id, reply_markup=m)

    elif call.data == "advanced":
        m = InlineKeyboardMarkup()
        m.row(InlineKeyboardButton("🔒 Protect", callback_data="protect"),
              InlineKeyboardButton("🔓 Unlock", callback_data="unlock"))
        m.row(InlineKeyboardButton("💧 Watermark", callback_data="watermark"))
        m.row(InlineKeyboardButton("🔙 Back", callback_data="back"))
        bot.edit_message_text("Advanced", cid, call.message.message_id, reply_markup=m)

    elif call.data in ["merge","img_pdf"]:
        user_data[cid] = {"mode": call.data, "files": []}
        bot.send_message(cid, "Send files then /done")

    elif call.data == "compress":
        user_data[cid] = {"mode": "compress"}
        bot.send_message(cid, "Send PDF to compress")

    elif call.data == "pdf_word":
        user_data[cid] = {"mode": "pdf_word"}
        bot.send_message(cid, "Send PDF")

    elif call.data == "protect":
        user_data[cid] = {"mode": "protect"}
        bot.send_message(cid, "Send PDF")

    elif call.data == "unlock":
        user_data[cid] = {"mode": "unlock"}
        bot.send_message(cid, "Send locked PDF")

    elif call.data == "watermark":
        user_data[cid] = {"mode": "watermark"}
        bot.send_message(cid, "Send PDF")

    elif call.data == "back":
        bot.edit_message_text("Main Menu", cid, call.message.message_id, reply_markup=main_menu())

# 📥 FILES
@bot.message_handler(content_types=['document','photo'])
def files(msg):
    cid = msg.chat.id
    if cid not in user_data: return

    mode = user_data[cid]["mode"]

    # MERGE / IMG
    if mode in ["merge","img_pdf"]:
        file_id = msg.document.file_id if msg.document else msg.photo[-1].file_id
        file_info = bot.get_file(file_id)
        data = bot.download_file(file_info.file_path)

        name = f"{cid}_{len(user_data[cid]['files'])}.dat"
        open(name,'wb').write(data)

        user_data[cid]["files"].append(name)
        bot.reply_to(msg,"Added")

    # COMPRESS
    elif mode == "compress":
        file_info = bot.get_file(msg.document.file_id)
        data = bot.download_file(file_info.file_path)

        open(f"{cid}.pdf",'wb').write(data)

        bot.send_message(cid,"⏳ Compressing...")

        reader = PdfReader(f"{cid}.pdf")
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        writer.write(f"{cid}_c.pdf")

        bot.send_document(cid, open(f"{cid}_c.pdf",'rb'))

        os.remove(f"{cid}.pdf")
        os.remove(f"{cid}_c.pdf")
        user_data.pop(cid)

    # PDF→WORD
    elif mode == "pdf_word":
        file_info = bot.get_file(msg.document.file_id)
        data = bot.download_file(file_info.file_path)

        open(f"{cid}.pdf",'wb').write(data)
        cv = Converter(f"{cid}.pdf")
        cv.convert(f"{cid}.docx")
        cv.close()

        bot.send_document(cid, open(f"{cid}.docx",'rb'))

        os.remove(f"{cid}.pdf")
        os.remove(f"{cid}.docx")
        user_data.pop(cid)

    # PROTECT / UNLOCK / WATERMARK
    elif mode in ["protect","unlock","watermark"]:
        file_info = bot.get_file(msg.document.file_id)
        data = bot.download_file(file_info.file_path)

        open(f"{cid}.pdf",'wb').write(data)

        if mode=="protect":
            user_data[cid]={"mode":"set_pass"}
            bot.send_message(cid,"Send password")

        elif mode=="unlock":
            user_data[cid]={"mode":"unlock_pass"}
            bot.send_message(cid,"Send password")

        elif mode=="watermark":
            user_data[cid]={"mode":"watermark_text"}
            bot.send_message(cid,"Send watermark text")

# 🔤 TEXT
@bot.message_handler(func=lambda m: True)
def text(msg):
    cid = msg.chat.id
    if cid not in user_data: return

    mode = user_data[cid]["mode"]

    if mode=="set_pass":
        pdf=pikepdf.open(f"{cid}.pdf")
        pdf.save(f"{cid}_lock.pdf",encryption=pikepdf.Encryption(owner=msg.text,user=msg.text))
        pdf.close()
        bot.send_document(cid,open(f"{cid}_lock.pdf",'rb'))

    elif mode=="unlock_pass":
        try:
            pdf=pikepdf.open(f"{cid}.pdf",password=msg.text)
            pdf.save(f"{cid}_un.pdf")
            pdf.close()
            bot.send_document(cid,open(f"{cid}_un.pdf",'rb'))
        except:
            bot.send_message(cid,"Wrong password")

    elif mode=="watermark_text":
        reader=PdfReader(f"{cid}.pdf")
        writer=PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        writer.add_metadata({"/Watermark": msg.text})

        writer.write(f"{cid}_wm.pdf")
        bot.send_document(cid,open(f"{cid}_wm.pdf",'rb'))

    # cleanup
    for f in os.listdir():
        if str(cid) in f:
            try: os.remove(f)
            except: pass

    user_data.pop(cid, None)

# DONE
@bot.message_handler(commands=['done'])
def done(msg):
    cid = msg.chat.id
    if cid not in user_data: return

    mode=user_data[cid]["mode"]

    if mode=="merge":
        merger=PdfMerger()
        for f in user_data[cid]["files"]:
            merger.append(f)
        out=f"{cid}_m.pdf"
        merger.write(out)
        merger.close()
        bot.send_document(cid,open(out,'rb'))

    elif mode=="img_pdf":
        out=f"{cid}_i.pdf"
        open(out,'wb').write(img2pdf.convert(user_data[cid]["files"]))
        bot.send_document(cid,open(out,'rb'))

    for f in user_data[cid]["files"]:
        os.remove(f)
    os.remove(out)
    user_data.pop(cid)

# RUN
def run_bot():
    bot.infinity_polling()

if __name__=="__main__":
    threading.Thread(target=run_web).start()
    run_bot()
