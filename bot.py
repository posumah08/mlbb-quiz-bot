from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from config import TOKEN, OWNER_ID
from questions import get_questions
import database

user_data = {}

# ================== COMMAND ==================

def start(update, context):
    if update.effective_chat.type == "private":
        update.message.reply_text("❌ Bot hanya untuk grup!")
        return

    chat_id = str(update.effective_chat.id)
    database.save_chat(chat_id)

    keyboard = [[InlineKeyboardButton("🎮 Mulai Quiz", callback_data="start")]]

    update.message.reply_text(
        "🔥 QUIZ MLBB\n\nKlik tombol untuk mulai!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== GAME ==================

def send_question(bot, chat_id):
    user = user_data[chat_id]
    q = user["questions"][user["index"]]

    keyboard = [
        [InlineKeyboardButton(opt, callback_data=f"ans_{i}")]
        for i, opt in enumerate(q["options"])
    ]

    bot.send_message(
        chat_id=int(chat_id),
        text=f"❓ {q['question']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def button(update, context):
    query = update.callback_query
    query.answer()

    chat_id = str(query.message.chat.id)
    name = query.from_user.first_name

    # ================= START GAME =================
    if query.data == "start":
        if chat_id in user_data and user_data[chat_id].get("active"):
            query.message.reply_text("⚠️ Game masih berjalan!")
            return

        user_data[chat_id] = {
            "index": 0,
            "score": 0,
            "active": True,
            "questions": get_questions()
        }

        query.message.reply_text("🔥 Quiz dimulai!")
        send_question(context.bot, chat_id)
        return

    # ================= CEK GAME =================
    if chat_id not in user_data or not user_data[chat_id].get("active"):
        return

    user = user_data[chat_id]
    ans = int(query.data.split("_")[1])
    q = user["questions"][user["index"]]

    # ================= JAWABAN =================
    if ans == q["answer"]:
        user["score"] += 10

        context.bot.send_message(
            chat_id=int(chat_id),
            text="JAWABAN BENAR ✅\n\n"
                 "Selamat kamu bertambah 10 Poin \n"
                 f"Total Poin kamu saat ini 👉 {user['score']}"
        )

    # ================= LANJUT =================
    user["index"] += 1

    if user["index"] < len(user["questions"]):
        send_question(context.bot, chat_id)
    else:
        # simpan leaderboard tanpa notif
        database.save_score(chat_id, name, user["score"])
        user["active"] = False

# ================== LEADERBOARD ==================

def leaderboard(update, context):
    data = database.get_leaderboard()
    text = "🏆 LEADERBOARD\n\n"

    for i, (name, score) in enumerate(data, 1):
        text += f"{i}. {name} - {score}\n"

    update.message.reply_text(text)

# ================== BROADCAST ==================

def broadcast(update, context):
    if update.effective_user.id != OWNER_ID:
        return

    msg = " ".join(context.args)
    for chat_id in database.get_chats():
        try:
            context.bot.send_message(chat_id=int(chat_id), text=msg)
        except:
            pass

# ================== RUN ==================

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("leaderboard", leaderboard))
dp.add_handler(CommandHandler("broadcast", broadcast))
dp.add_handler(CallbackQueryHandler(button))

updater.start_polling()
updater.idle()
