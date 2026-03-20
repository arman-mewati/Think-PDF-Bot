from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import pikepdf
import os

user_data = {}

def register(bot):

    @bot.callback_query_handler(func=lambda c: c.data == "advanced")
    def menu(call):
        m = InlineKeyboardMarkup()
        m.row(
            InlineKeyboardButton("Protect", callback_data="protect"),
            InlineKeyboardButton("Unlock", callback_data="unlock")
        )
        bot.edit_message_text("Advanced Tools", call.message.chat.id, call.message.message_id, reply_markup=m)

    @bot.callback_query_handler(func=lambda c: c.data == "protect")
    def protect(call):
        user_data[call.message.chat.id] = "protect"
        bot.send_message(call.message.chat.id, "Send PDF")

    @bot.callback_query_handler(func=lambda c: c.data == "unlock")
    def unlock(call):
        user_data[call.message.chat.id] = "unlock"
        bot.send_message(call.message.chat.id, "Send PDF")

    @bot.message_handler(content_types=['document'])
    def file(msg):
        cid = msg.chat.id

        if cid not in user_data:
            return

        file_info = bot.get_file(msg.document.file_id)
        data = bot.download_file(file_info.file_path)

        open(f"{cid}.pdf", 'wb').write(data)

        if user_data[cid] == "protect":
            user_data[cid] = "set_pass"
            bot.send_message(cid, "Send password")

        elif user_data[cid] == "unlock":
            user_data[cid] = "unlock_pass"
            bot.send_message(cid, "Send password")

    @bot.message_handler(func=lambda m: True)
    def text(msg):
        cid = msg.chat.id

        if cid not in user_data:
            return

        if user_data[cid] == "set_pass":
            pdf = pikepdf.open(f"{cid}.pdf")
            pdf.save(f"{cid}_lock.pdf", encryption=pikepdf.Encryption(owner=msg.text, user=msg.text))
            pdf.close()

            bot.send_document(cid, open(f"{cid}_lock.pdf", 'rb'))

        elif user_data[cid] == "unlock_pass":
            try:
                pdf = pikepdf.open(f"{cid}.pdf", password=msg.text)
                pdf.save(f"{cid}_unlock.pdf")
                pdf.close()

                bot.send_document(cid, open(f"{cid}_unlock.pdf", 'rb'))
            except:
                bot.send_message(cid, "Wrong password")

        for f in os.listdir():
            if str(cid) in f:
                try: os.remove(f)
                except: pass

        user_data.pop(cid, None)
