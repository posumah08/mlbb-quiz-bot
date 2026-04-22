from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from config import TOKEN
from questions import QUESTIONS
import database
import random

user_data = {}

# ================== UTIL ==================

def get_random_question():
    return random.choice(QUESTIONS)

def send_next_question(context):
    job = context.job
    chat_id = job.context
    send_question(context.bot, chat_id)

# ================== COMMAND ==================

def start(update, context):
    chat_id = str(update.effective_chat.id)

    # 🔥 kalau masih jalan
    if chat_id in user_data and user_data[chat_id].get("active"):
        update.message.reply_text("⚠️ Game masih berjalan!")
        return

    user_data[chat_id] = {
        "active": True,
        "current_q": None,
        "last_q_msg": None,
        "answered": False
    }

    update.message.reply_text("🔥 Tebak Gambar MLBB Dimulai!")
    send_question(context.bot, chat_id)

# ================== GAME ==================

def send_question(bot, chat_id):
    user = user_data[chat_id]
    q = get_random_question()

    user["current_q"] = q
    user["answered"] = False

    msg = bot.send_photo(
        chat_id=int(chat_id),
        photo=open(q["image"], "rb"),
        caption="❓ Tebak hero ini!"
    )

    user["last_q_msg"] = msg.message_id

# ================== JAWAB ==================

def answer(update, context):
    chat_id = str(update.effective_chat.id)
    user_id = str(update.effective_user.id)
    name = update.effective_user.first_name
    text = update.message.text.lower().strip()

    if chat_id not in user_data:
        return

    user = user_data[chat_id]

    if not user.get("active"):
        return

    # ❗ harus reply ke gambar
    if not update.message.reply_to_message:
        return

    if update.message.reply_to_message.message_id != user.get("last_q_msg"):
        return

    # ❗ kalau sudah dijawab orang lain
    if user.get("answered"):
        return

    q = user.get("current_q")
    if not q:
        return

    correct = q["answer"].lower()

    # ================= CEK =================
    if text == correct:
        user["answered"] = True

        try:
            database.add_global_score(user_id, name, 10)
            database.add_group_score(chat_id, user_id, name, 10)
            score = database.get_user_score(user_id)
        except:
            score = "?"

        context.bot.send_message(
            chat_id=int(chat_id),
            text=f"⚡ {name} benar!\n+10 poin\nTotal 👉 {score}"
        )

        # ⏳ lanjut soal 3 detik
        context.job_queue.run_once(send_next_question, 3, context=chat_id)

        # 🧹 hapus soal lama
        try:
            context.bot.delete_message(chat_id=int(chat_id), message_id=user["last_q_msg"])
        except:
            pass

# ================== NEXT ==================

def next_q(update, context):
    chat_id = str(update.effective_chat.id)

    if chat_id not in user_data:
        return

    if not user_data[chat_id].get("active"):
        return

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
