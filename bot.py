from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
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

    keyboard = [[InlineKeyboardButton("🎮 Mulai Quiz", callback_data="start")]]

    msg = context.bot.send_message(
        chat_id=int(chat_id),
        text="Klik tombol untuk mulai!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    user_data[chat_id] = {
        "menu_msg": msg.message_id,
        "active": False
    }

# ================== GAME ==================

def send_question(bot, chat_id):
    if chat_id not in user_data:
        return

    q = get_random_question()
    user_data[chat_id]["current_q"] = q

    keyboard = [
        [InlineKeyboardButton(opt, callback_data=f"ans_{i}")]
        for i, opt in enumerate(q["options"])
    ]

    msg = bot.send_message(
        chat_id=int(chat_id),
        text=f"❓ {q['question']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    user_data[chat_id]["last_q_msg"] = msg.message_id

def button(update, context):
    query = update.callback_query
    query.answer()

    chat_id = str(query.message.chat.id)
    user_id = str(query.from_user.id)
    name = query.from_user.first_name

    # ================= START =================
    if query.data == "start":

        try:
            menu_id = user_data.get(chat_id, {}).get("menu_msg")
            if menu_id:
                context.bot.delete_message(chat_id=int(chat_id), message_id=menu_id)
        except:
            pass

        user_data[chat_id] = {
            "active": True,
            "current_q": None,
            "last_q_msg": None
        }

        send_question(context.bot, chat_id)
        return

    # ================= CEK =================
    if chat_id not in user_data:
        return

    user = user_data[chat_id]

    if not user.get("active"):
        return

    if not query.data.startswith("ans_"):
        return

    q = user.get("current_q")

    if not q:
        send_question(context.bot, chat_id)
        return

    ans = int(query.data.split("_")[1])

    # hapus soal lama
    try:
        last = user.get("last_q_msg")
        if last:
            context.bot.delete_message(chat_id=int(chat_id), message_id=last)
    except:
        pass

    # ================= JAWABAN =================
    correct = q["answer"]

    try:
        if isinstance(correct, str):
            if correct.upper() in ["A","B","C","D"]:
                correct = ["A","B","C","D"].index(correct.upper())
            else:
                correct = q["options"].index(correct)
    except:
        correct = -1

    if ans == correct:
        try:
            database.add_global_score(user_id, name, 10)
            database.add_group_score(chat_id, user_id, name, 10)
            score = database.get_user_score(user_id)
        except:
            score = "?"

        context.bot.send_message(
            chat_id=int(chat_id),
            text=f"JAWABAN BENAR ✅\n+10 poin\nTotal Poin kamu 👉 {score}"
        )
    else:
        context.bot.send_message(
            chat_id=int(chat_id),
            text="SALAH ❌"
        )

    # ⏳ jeda 3 detik TANPA FREEZE
    context.job_queue.run_once(send_next_question, 3, context=chat_id)

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
    dp.add_handler(CallbackQueryHandler(button))

    print("BOT RUNNING...")

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
