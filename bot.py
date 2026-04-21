from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from config import TOKEN
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

    if chat_id in user_data and user_data[chat_id].get("active"):
        update.message.reply_text("⚠️ Game masih berjalan!")
        return

    keyboard = [[InlineKeyboardButton("🎮 Mulai Quiz", callback_data="start")]]

    update.message.reply_text(
        "🔥 QUIZ MLBB (MODE TERCEPAT)\n\nKlik tombol untuk mulai!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== GAME ==================

def send_question(bot, chat_id):
    user = user_data[chat_id]
    q = get_random_question()

    user["current_q"] = q
    user["answered"] = False  # 🔥 reset rebutan

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
            "last_q_msg": None,
            "answered": False
        }

        query.message.reply_text("🔥 Quiz dimulai (REBUTAN)!")
        send_question(context.bot, chat_id)
        return

    # ================= CEK GAME =================
    if chat_id not in user_data or not user_data[chat_id].get("active"):
        return

    user = user_data[chat_id]

    if not query.data.startswith("ans_"):
        return

    # 🔥 kalau sudah ada yang jawab duluan
    if user.get("answered"):
        query.answer("❌ Sudah dijawab!", show_alert=True)
        return

    ans = int(query.data.split("_")[1])
    q = user["current_q"]

    # 🔥 kunci jawaban pertama
    user["answered"] = True

    # 🔥 matikan tombol
    try:
        query.edit_message_reply_markup(reply_markup=None)
    except:
        pass

    # ================= HASIL =================
    if ans == q["answer"]:
        database.add_global_score(user_id, name, 10)

        context.bot.send_message(
            chat_id=int(chat_id),
            text=f"⚡ {name} tercepat!\n+10 poin"
        )
    else:
        context.bot.send_message(
            chat_id=int(chat_id),
            text=f"❌ {name} salah!"
        )

    time.sleep(3)

    # 🔥 hapus soal lama
    try:
        context.bot.delete_message(chat_id=int(chat_id), message_id=user["last_q_msg"])
    except:
        pass

    # lanjut soal baru
    send_question(context.bot, chat_id)

# ================== RUN ==================

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CallbackQueryHandler(button))

updater.start_polling()
updater.idle()
