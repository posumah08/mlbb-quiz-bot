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

def valid_command(text):
    if not text:
        return True
    text = text.lower()
    return not ("@" in text and "@quizmlbb_bot" not in text)

# ================== COMMAND ==================

def start(update, context):
    text = update.message.text
    chat_id = str(update.effective_chat.id)

    if not valid_command(text):
        return

    if update.effective_chat.type == "private":
        update.message.reply_text("❌ Bot hanya untuk grup!")
        return

    database.save_chat(chat_id)

    if chat_id in user_data and user_data[chat_id].get("active"):
        context.bot.send_message(chat_id=int(chat_id), text="⚠️ Game masih berjalan!")
        return

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
    user = user_data.get(chat_id)
    if not user:
        return

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

        # hapus menu bot
        try:
            context.bot.delete_message(
                chat_id=int(chat_id),
                message_id=user_data.get(chat_id, {}).get("menu_msg")
            )
        except:
            pass

        user_data[chat_id] = {
            "active": True,
            "current_q": None,
            "last_q_msg": None
        }

        send_question(context.bot, chat_id)
        return

    # ================= CEK GAME =================
    if chat_id not in user_data or not user_data[chat_id].get("active"):
        return

    if not query.data.startswith("ans_"):
        return

    user = user_data[chat_id]
    ans = int(query.data.split("_")[1])
    q = user.get("current_q")

    if not q:
        return

    # hapus soal lama
    try:
        context.bot.delete_message(
            chat_id=int(chat_id),
            message_id=user.get("last_q_msg")
        )
    except:
        pass

    # ================= JAWABAN =================
    if ans == q["answer"]:

        database.add_global_score(user_id, name, 10)
        database.add_group_score(chat_id, user_id, name, 10)

        context.bot.send_message(
            chat_id=int(chat_id),
            text=f"JAWABAN BENAR ✅\n+10 poin\nTotal Poin kamu 👉 {database.get_user_score(user_id)}"
        )

        time.sleep(2)

    send_question(context.bot, chat_id)

# ================== NEXT ==================

def next_q(update, context):
    text = update.message.text
    chat_id = str(update.effective_chat.id)
    message_id = update.message.message_id

    if not valid_command(text):
        return

    # hapus command /next
    try:
        context.bot.delete_message(chat_id=int(chat_id), message_id=message_id)
    except:
        pass

    if chat_id not in user_data or not user_data[chat_id].get("active"):
        return

    # hapus soal lama
    try:
        context.bot.delete_message(
            chat_id=int(chat_id),
            message_id=user_data[chat_id].get("last_q_msg")
        )
    except:
        pass

    send_question(context.bot, chat_id)

# ================== LEADERBOARD GLOBAL ==================

def leaderboard(update, context):
    text = update.message.text

    if not valid_command(text):
        return

    data = database.get_global_leaderboard()

    text_out = "🏆 GLOBAL LEADERBOARD\n\n"
    for i, (name, score) in enumerate(data, 1):
        text_out += f"{i}. {name} - {score}\n"

    update.message.reply_text(text_out)

# ================== TOP GRUP ==================

def topgrup(update, context):
    text = update.message.text
    chat_id = str(update.effective_chat.id)

    if not valid_command(text):
        return

    data = database.get_group_leaderboard(chat_id)

    text_out = "🏆 LEADERBOARD GRUP\n\n"
    for i, (name, score) in enumerate(data, 1):
        text_out += f"{i}. {name} - {score}\n"

    update.message.reply_text(text_out)

# ================== STATS USER ==================

def stats(update, context):
    text = update.message.text
    user_id = str(update.effective_user.id)

    if not valid_command(text):
        return

    score = database.get_user_score(user_id)

    update.message.reply_text(f"📊 Total Poin kamu: {score}")

# ================== RUN ==================

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("next", next_q))
    dp.add_handler(CommandHandler("leaderboard", leaderboard))
    dp.add_handler(CommandHandler("topgrup", topgrup))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CallbackQueryHandler(button))

    print("BOT RUNNING...")

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
