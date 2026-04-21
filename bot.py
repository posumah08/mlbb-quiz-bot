import os
import random
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

TOKEN = os.getenv("TOKEN")

DATA_FILE = "leaderboard.json"

questions = [
    {"question": "Hero lifesteal tinggi?", "options": ["Alucard","Layla","Miya","Eudora"], "answer": 0},
    {"question": "Ultimate Harith?", "options": ["Chrono Dash","Zaman Force","Black Shoes","Time Rift"], "answer": 2},
    {"question": "Hero sniper MLBB?", "options": ["Layla","Tank","Fighter","Mage"], "answer": 0},
    {"question": "Role Tigreal?", "options": ["Mage","Tank","Assassin","Marksman"], "answer": 1},
    {"question": "Hero ninja MLBB?", "options": ["Hayabusa","Franco","Balmond","Clint"], "answer": 0}
]

user_data = {}

# load leaderboard
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

# save leaderboard
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

leaderboard = load_data()

def start(update, context):
    keyboard = [[InlineKeyboardButton("🎮 Mulai Quiz", callback_data="start")]]
    update.message.reply_text(
        "🔥 QUIZ MLBB\n\nKetik /leaderboard untuk lihat ranking",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def button(update, context):
    query = update.callback_query
    query.answer()
    chat_id = str(query.message.chat.id)
    name = query.from_user.first_name

    if query.data == "start":
        user_data[chat_id] = {
            "index": 0,
            "score": 0,
            "questions": random.sample(questions, len(questions))
        }
        send_question(query)

    elif query.data.startswith("ans_"):
        ans = int(query.data.split("_")[1])
        user = user_data[chat_id]
        q = user["questions"][user["index"]]

        if ans == q["answer"]:
            user["score"] += 1
            query.message.reply_text("✅ Benar!")
        else:
            query.message.reply_text("❌ Salah!")

        user["index"] += 1

        if user["index"] < len(user["questions"]):
            send_question(query)
        else:
            score = user["score"]

            # simpan ke leaderboard
            if chat_id not in leaderboard or leaderboard[chat_id]["score"] < score:
                leaderboard[chat_id] = {"name": name, "score": score}
                save_data(leaderboard)

            keyboard = [[InlineKeyboardButton("🔄 Main Lagi", callback_data="start")]]
            query.message.reply_text(
                f"🏆 Quiz selesai!\nSkor: {score}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

def send_question(query):
    chat_id = str(query.message.chat.id)
    user = user_data[chat_id]
    q = user["questions"][user["index"]]

    keyboard = [
        [InlineKeyboardButton(opt, callback_data=f"ans_{i}")]
        for i, opt in enumerate(q["options"])
    ]

    query.message.reply_text(
        f"❓ {q['question']}\n\nSkor: {user['score']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def show_leaderboard(update, context):
    if not leaderboard:
        update.message.reply_text("Belum ada data 😢")
        return

    sorted_lb = sorted(leaderboard.values(), key=lambda x: x["score"], reverse=True)

    text = "🏆 LEADERBOARD TOP 10\n\n"
    for i, user in enumerate(sorted_lb[:10], start=1):
        text += f"{i}. {user['name']} - {user['score']}\n"

    update.message.reply_text(text)

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("leaderboard", show_leaderboard))
dp.add_handler(CallbackQueryHandler(button))

updater.start_polling()
updater.idle()
