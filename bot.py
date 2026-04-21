from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from config import TOKEN, OWNER_ID
from questions import QUESTIONS
import database
import random
import time

user_data = {}

# ================== UTIL ==================

def get_random_question():
    return random.choice(QUESTIONS)

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
        "🔥 QUIZ MLBB (ENDLESS)\n\nKlik tombol untuk mulai!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== GAME ==================

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
    user_id = str(query.from_user.id)
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
            "active": True,
            "current_q": None,
            "last_q_msg": None
        }

        query.message.reply_text("🔥 Quiz dimulai!")
        send_question(context.bot, chat_id)
        return

    # ================= CEK GAME =================
    if chat_id not in user_data or not user_data[chat_id].get("active"):
        return

    if not query.data.startswith("ans_"):
        return

    user = user_data[chat_id]
    ans = int(query.data.split("_")[1])
    q = user["current_q"]

    # hapus soal lama
    try:
        context.bot.delete_message(chat_id=int(chat_id), message_id=user["last_q_msg"])
    except:
        pass

    # ================= JAWABAN =================
    if ans == q["answer"]:

        # 🔥 simpan GLOBAL
        database.add_global_score(user_id, name, 10)

        # 🔥 simpan GRUP
        database.add_group_score(chat_id, user_id, name, 10)

        context.bot.send_message(
            chat_id=int(chat_id),
            text=f"JAWABAN BENAR ✅\n+10 poin\nTotal kamu 👉 {database.get_user_score(user_id)}"
        )

        time.sleep(3)

    send_question(context.bot, chat_id)

# ================== NEXT ==================

def next_q(update, context):
    text = update.message.text
    chat_id = str(update.effective_chat.id)

    if "@quizmlbb_bot" not in text:
        return

    if chat_id not in user_data or not user_data[chat_id].get("active"):
        return

    # hapus soal lama
    try:
        context.bot.delete_message(
            chat_id=int(chat_id),
            message_id=user_data[chat_id]["last_q_msg"]
        )
    except:
        pass

    send_question(context.bot, chat_id)

# ================== LEADERBOARD GLOBAL ==================

def leaderboard(update, context):
    text_cmd = update.message.text
    if "@quizmlbb_bot" not in text_cmd:
        return

    data = database.get_global_leaderboard()

    text = "🏆 GLOBAL LEADERBOARD\n\n"
    for i, (name, score) in enumerate(data, 1):
        text += f"{i}. {name} - {score}\n"

    update.message.reply_text(text)

# ================== TOP GRUP ==================

def topgrup(update, context):
    text_cmd = update.message.text
    chat_id = str(update.effective_chat.id)

    if "@quizmlbb_bot" not in text_cmd:
        return

    data = database.get_group_leaderboard(chat_id)

    text = "🏆 LEADERBOARD GRUP\n\n"
    for i, (name, score) in enumerate(data, 1):
        text += f"{i}. {name} - {score}\n"

    update.message.reply_text(text)

# ================== STATS USER ==================

def stats(update, context):
    text_cmd = update.message.text
    user_id = str(update.effective_user.id)

    if "@quizmlbb_bot" not in text_cmd:
        return

    score = database.get_user_score(user_id)

    update.message.reply_text(f"📊 Total poin kamu: {score}")

# ================== RUN ==================

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("next", next_q))
dp.add_handler(CommandHandler("leaderboard", leaderboard))
dp.add_handler(CommandHandler("topgrup", topgrup))
dp.add_handler(CommandHandler("stats", stats))
dp.add_handler(CallbackQueryHandler(button))

updater.start_polling()
updater.idle()
