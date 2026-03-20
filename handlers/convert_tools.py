from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from pdf2docx import Converter
import img2pdf
import os

user_data = {}

def register(bot):

    @bot.callback_query_handler(func=lambda c: c.data == "convert")
    def menu(call):
        m = InlineKeyboardMarkup()
        m.row(
            InlineKeyboardButton("PDF → Word", callback_data="pdf_word"),
            InlineKeyboardButton("Image → PDF", callback_data="img_pdf")
        )
        bot.edit_message_text("Convert Tools", call.message.chat.id, call.message.message_id, reply_markup=m)

    @bot.callback_query_handler(func=lambda c: c.data == "pdf_word")
    def pdf_word(call):
        user_data[call.message.chat.id] = "pdf_word"
        bot.send_message(call.message.chat.id, "Send PDF")

    @bot.callback_query_handler(func=lambda c: c.data == "img_pdf")
    def img_pdf(call):
        user_data[call.message.chat.id] = []
        bot.send_message(call.message.chat.id, "Send images then /done")

    @bot.message_handler(content_types=['document','photo'])
    def handle(msg):
        cid = msg.chat.id

        if cid not in user_data:
            return

        # PDF → WORD
        if user_data[cid] == "pdf_word":
            file_info = bot.get_file(msg.document.file_id)
            data = bot.download_file(file_info.file_path)

            open(f"{cid}.pdf", 'wb').write(data)

            cv = Converter(f"{cid}.pdf")
            cv.convert(f"{cid}.docx")
            cv.close()

            bot.send_document(cid, open(f"{cid}.docx", 'rb'))

            os.remove(f"{cid}.pdf")
            os.remove(f"{cid}.docx")
            user_data.pop(cid)

        # IMAGE → PDF
        elif isinstance(user_data[cid], list):
            file_id = msg.photo[-1].file_id if msg.photo else msg.document.file_id
            file_info = bot.get_file(file_id)
            data = bot.download_file(file_info.file_path)

            name = f"{cid}_{len(user_data[cid])}.jpg"
            open(name, 'wb').write(data)

            user_data[cid].append(name)

    @bot.message_handler(commands=['done'])
    def done(msg):
        cid = msg.chat.id

        if cid not in user_data or not isinstance(user_data[cid], list):
            return

        out = f"{cid}.pdf"
        open(out, 'wb').write(img2pdf.convert(user_data[cid]))

        bot.send_document(cid, open(out, 'rb'))

        for f in user_data[cid]:
            os.remove(f)

        os.remove(out)
        user_data.pop(cid)
