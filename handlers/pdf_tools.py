from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from PyPDF2 import PdfMerger
import os

user_data = {}

def register(bot):

    @bot.callback_query_handler(func=lambda c: c.data == "pdf_tools")
    def menu(call):
        m = InlineKeyboardMarkup()
        m.row(InlineKeyboardButton("📄 Merge", callback_data="merge"))
        bot.edit_message_text("PDF Tools", call.message.chat.id, call.message.message_id, reply_markup=m)

    @bot.callback_query_handler(func=lambda c: c.data == "merge")
    def merge_start(call):
        user_data[call.message.chat.id] = []
        bot.send_message(call.message.chat.id, "Send PDFs then /done")

    @bot.message_handler(content_types=['document'])
    def handle_pdf(msg):
        cid = msg.chat.id

        if cid not in user_data:
            return

        file_info = bot.get_file(msg.document.file_id)
        data = bot.download_file(file_info.file_path)

        name = f"{cid}_{len(user_data[cid])}.pdf"
        open(name, 'wb').write(data)

        user_data[cid].append(name)
        bot.reply_to(msg, "Added")

    @bot.message_handler(commands=['done'])
    def done(msg):
        cid = msg.chat.id

        if cid not in user_data or len(user_data[cid]) < 2:
            return

        merger = PdfMerger()
        for f in user_data[cid]:
            merger.append(f)

        out = f"{cid}_merged.pdf"
        merger.write(out)
        merger.close()

        bot.send_document(cid, open(out, 'rb'))

        for f in user_data[cid]:
            os.remove(f)

        os.remove(out)
        user_data.pop(cid)
