from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import TOKEN
from questions import QUESTIONS
import database
import random
import os

user_data = {}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ================= UTIL ==================

def valid_command(text):
    if not text:
        return True
    text = text.lower()
    return not ("@" in text and "@quizmlbb_bot" not in text)

def group_only(update):
    return update.effective_chat.type in ["group", "supergroup"]

def send_next_question(context):
    chat_id = context.job.context
    send_question(context.bot, chat_id)

# ================= START ==================

def start(update, context):
    # ================= PRIVATE =================
    if update.effective_chat.type == "private":

        keyboard = [
            [InlineKeyboardButton("👤 Dev", url="https://t.me/yasanyamagurai")],
            [InlineKeyboardButton("➕ Tambahkan ke GRUP", url="https://t.me/quizmlbb_bot?startgroup=true")]
        ]

        update.message.reply_text(
            "Halo Player, Selamat bergabung di QUIZ MLBB ID.\n"
            "Tambahkan Bot ini di GRUP TELEGRAM untuk Mulai Permainan.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # ================= GROUP =================
    if not group_only(update):
        return

    chat_id = str(update.effective_chat.id)
    text = update.message.text

    if not valid_command(text):
        return

    if chat_id in user_data and user_data[chat_id].get("active"):
        update.message.reply_text("⚠️ Game masih berjalan!")
        return

    user_data[chat_id] = {
        "active": True,
        "questions": random.sample(QUESTIONS, len(QUESTIONS)),
        "index": 0,
        "current_q": None,
        "last_q_msg": None,
        "answered": False
    }

    send_question(context.bot, chat_id)

# ================= GAME ==================

def send_question(bot, chat_id):
    if chat_id not in user_data:
        return

    user = user_data[chat_id]

    if user["index"] >= len(user["questions"]):
        user["questions"] = random.sample(QUESTIONS, len(QUESTIONS))
        user["index"] = 0

    q = user["questions"][user["index"]]
    user["index"] += 1

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
        bot.send_message(chat_id=int(chat_id), text="❌ Gambar tidak ditemukan!")

# ================= JAWAB ==================

def answer(update, context):
    if not group_only(update):
        return

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

    if update.message.reply_to_message:
        if update.message.reply_to_message.message_id != user.get("last_q_msg"):
            return

    if user.get("answered"):
        return

    q = user.get("current_q")
    if not q:
        return

    correct = q["answer"].lower()

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
            text=f"🔥 JAWABAN BENAR 🔥\nMMR +10\nTOTAL MMR KAMU 👉 {score} MMR\nRANK : "
        )

        try:
            last = user.get("last_q_msg")
            if last:
                context.bot.delete_message(chat_id=int(chat_id), message_id=last)
        except:
            pass

        context.job_queue.run_once(send_next_question, 3, context=chat_id)

# ================= NEXT ==================

def next_q(update, context):
    if not group_only(update):
        return

    chat_id = str(update.effective_chat.id)
    text = update.message.text

    if not valid_command(text):
        return

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

# ================= STATS ==================

def stats(update, context):
    if not group_only(update):
        return

    text = update.message.text
    if not valid_command(text):
        return

    user_id = str(update.effective_user.id)

    score = 0
    try:
        score = database.get_user_score(user_id)
    except:
        pass

    update.message.reply_text(
        f"Stats\nMMR kamu sekarang 👉 {score}\nRANK :"
    )

# ================= LEADERBOARD ==================

def leaderboard(update, context):
    if not group_only(update):
        return

    data = database.get_global_leaderboard()

    text = "🏆 GLOBAL LEADERBOARD\n\n"
    for i, (name, score) in enumerate(data, 1):
        text += f"{i}. {name} - {score}\n"

    update.message.reply_text(text)

def topgrup(update, context):
    if not group_only(update):
        return

    chat_id = str(update.effective_chat.id)
    data = database.get_group_leaderboard(chat_id)

    text = "🏆 LEADERBOARD GRUP\n\n"
    for i, (name, score) in enumerate(data, 1):
        text += f"{i}. {name} - {score}\n"

    update.message.reply_text(text)

# ================= RUN ==================

def main():
    database.init_db()

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("next", next_q))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("leaderboard", leaderboard))
    dp.add_handler(CommandHandler("topgrup", topgrup))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, answer))

    print("BOT RUNNING...")

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
