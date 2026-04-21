from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from config import TOKEN, OWNER_ID
from questions import QUESTIONS
import database
import random
import time

user_data = {}

# ================== COMMAND ==================

def start(update, context):
    text = update.message.text
    chat_id = str(update.effective_chat.id)

    if "@quizmlbb_bot" not in text:
        return

    if update.effective_chat.type == "private":
        update.message.reply_text("❌ Bot hanya untuk grup!")
        return

    database.save_chat(chat_id)

    if chat_id in user_data and user_data[chat_id].get("active"):
        update.message.reply_text("⚠️ Game masih berjalan!")
        return

    keyboard = [[InlineKeyboardButton("🎮 Mulai Quiz", callback_data="start")]]

    update.message.reply_text(
        "🔥 QUIZ MLBB (ENDLESS MODE)\n\nKlik tombol untuk mulai!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== GAME ==================

def get_random_question():
    return random.choice(QUESTIONS)

def send_question(bot, chat_id):
    user = user_data[chat_id]
    q = get_random_question()

    user["current_q"] = q

    keyboard = [
        [InlineKeyboardButton(opt, callback_data=f"ans_{i}")]
        for i, opt in enumerate(q["options"])
    ]

    msg = bot.send_message(
        chat_id=int(chat_id),
        text=f"❓ {q['question']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    user["last_q_msg"] = msg.message_id

def button(update, context):
    query = update.callback_query
    query.answer()

    chat_id = str(query.message.chat.id)
    name = query.from_user.first_name

    # ================= START =================
    if query.data == "start":

        if chat_id in user_data and user_data[chat_id].get("active"):
            query.answer("Game masih berjalan!", show_alert=True)
            return

        try:
            query.edit_message_reply_markup(reply_markup=None)
        except:
            pass

        user_data[chat_id] = {
            "score": 0,
            "active": True,
            "current_q": None,
            "last_q_msg": None
        }

        query.message.reply_text("🔥 Quiz dimulai (ENDLESS MODE)!")
        send_question(context.bot, chat_id)
        return

    # ================= CEK GAME =================
    if chat_id not in user_data or not user_data[chat_id].get("active"):
        return

    user = user_data[chat_id]

    if not query.data.startswith("ans_"):
        return

    ans = int(query.data.split("_")[1])
    q = user["current_q"]

    # 🔥 hapus soal sebelumnya
    try:
        context.bot.delete_message(chat_id=int(chat_id), message_id=user["last_q_msg"])
    except:
        pass

    # ================= JAWABAN =================
    if ans == q["answer"]:
        user["score"] += 10

        context.bot.send_message(
            chat_id=int(chat_id),
            text="JAWABAN BENAR ✅\n\n"
                 "Selamat kamu bertambah 10 Poin \n"
                 f"Total Poin kamu saat ini 👉 {user['score']}"
        )

        time.sleep(3)

    # 🔥 LANGSUNG LANJUT TANPA BATAS
    send_question(context.bot, chat_id)
