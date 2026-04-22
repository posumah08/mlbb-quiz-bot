from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from config import TOKEN
from questions import QUESTIONS
import database
import random
import os

user_data = {}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ================== UTIL ==================

def get_random_question():
    return random.choice(QUESTIONS)

def valid_command(text):
    if not text:
        return True
    text = text.lower()
    return not ("@" in text and "@quizmlbb_bot" not in text)

# ================== START ==================

def start(update, context):
    chat_id = str(update.effective_chat.id)
    text = update.message.text

    if not valid_command(text):
        return

    # kalau game masih jalan
    if chat_id in user_data and user_data[chat_id].get("active"):
        update.message.reply_text("⚠️ Game masih berjalan!")
        return

    user_data[chat_id] = {
        "active": True,
        "current_q": None,
        "last_q_msg": None,
        "answered": False
    }

    # langsung kirim soal (tanpa teks)
    send_question(context.bot, chat_id)

# ================== GAME ==================

def send_question(bot, chat_id):
    if chat_id not in user_data:
        return

    user = user_data[chat_id]
    q = get_random_question()

    user["current_q"] = q
    user["answered"] = False

    image_path = os.path.join(BASE_DIR, q["image"])

    try:
        with open(image_path, "rb") as img:
            msg = bot.send_photo(
                chat_id=int(chat_id),
                photo=img,
                caption="❓ Tebak hero ini!"
            )

        user["last_q_msg"] = msg.message_id

    except Exception as e:
        print("ERROR GAMBAR:", e)

        bot.send_message(
            chat_id=int(chat_id),
            text="❌ Gambar tidak ditemukan!"
        )

# ================== JAWAB ==================

def answer(update, context):
    if not update.message or not update.message.text:
        return

    chat_id = str(update.effective_chat.id)
    user_id = str(update.effective_user.id)
    name = update.effective_user.first_name
    text = update.message.text.lower().strip()

    if chat_id not in user_data:
        return

    user = user_data[chat_id]

    if not user.get("active"):
        return

    # optional reply check
    if update.message.reply_to_message:
        if update.message.reply_to_message.message_id != user.get("last_q_msg"):
            return

    # kalau sudah dijawab
    if user.get("answered"):
        return

    q = user.get("current_q")
    if not q:
        return

    correct = q["answer"].lower()

    # ================= CEK =================
    if text == correct:
        user["answered"] = True

        score = 0
        try:
            database.add_global_score(user_id, name, 10)
            database.add_group_score(chat_id, user_id, name, 10)
            score = database.get_user_score(user_id) or 0
        except Exception as e:
            print("DB ERROR:", e)

        context.bot.send_message(
            chat_id=int(chat_id),
            text=f"🔥 JAWABAN BENAR 🔥\nMMR +10\nTOTAL MMR KAMU 👉 {score}"
        )

        # hapus soal lama
        try:
            last = user.get("last_q_msg")
            if last:
                context.bot.delete_message(chat_id=int(chat_id), message_id=last)
        except:
            pass

# ================== NEXT ==================

def next_q(update, context):
    chat_id = str(update.effective_chat.id)
    text = update.message.text

    if not valid_command(text):
        return

    if chat_id not in user_data:
        return

    if not user_data[chat_id].get("active"):
        return

    # hapus soal lama
    try:
        last = user_data[chat_id].get("last_q_msg")
        if last:
            context.bot.delete_message(chat_id=int(chat_id), message_id=last)
    except:
        pass

    send_question(context.bot, chat_id)

# ================== RUN ==================

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("next", next_q))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, answer))

    print("BOT RUNNING...")

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
