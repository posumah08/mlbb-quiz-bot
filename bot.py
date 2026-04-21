import os
import random
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

TOKEN = os.getenv("TOKEN")
OWNER_ID = 6776834334

DATA_FILE = "leaderboard.json"
CHAT_FILE = "chats.json"

questions = [
    {"question": "Hero lifesteal tinggi?", "options": ["Alucard","Layla","Miya","Eudora"], "answer": 0},
    {"question": "Ultimate Harith?", "options": ["Chrono Dash","Zaman Force","Black Shoes","Time Rift"], "answer": 2}
]

user_data = {}

# load/save leaderboard
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# load/save chat id
def load_chats():
    try:
        with open(CHAT_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_chats(data):
    with open(CHAT_FILE, "w") as f:
        json.dump(data, f)

leaderboard = load_data()
chat_list = load_chats()

# cek grup
def is_group(update):
    return update.effective_chat.type in ["group", "supergroup"]

def start(update, context):
    chat_id = str(update.effective_chat.id)

    if not is_group(update):
        update.message.reply_text("❌ Bot ini hanya bisa digunakan di GRUP!")
        return

    # simpan chat
    if chat_id not in chat_list:
        chat_list.append(chat_id)
        save_chats(chat_list)

    keyboard = [[InlineKeyboardButton("🎮 Mulai Quiz", callback_data="start")]]
    update.message.reply_text("🔥 QUIZ MLBB (GROUP MODE)", reply_markup=InlineKeyboardMarkup(keyboard))

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
            query.message.reply_text(f"✅ {name} BENAR!")
        else:
            query.message.reply_text(f"❌ {name} SALAH!")

        user["index"] += 1

        if user["index"] < len(user["questions"]):
            send_question(query)
        else:
            score = user["score"]

            if chat_id not in leaderboard or leaderboard[chat_id]["score"] < score:
                leaderboard[chat_id] = {"name": name, "score": score}
                save_data(leaderboard)

            query.message.reply_text(f"🏆 Selesai!\nSkor: {score}")

def send_question(query):
    chat_id = str(query.message.chat.id)
    user = user_data[chat_id]
    q = user["questions"][user["index"]]

    keyboard = [
        [InlineKeyboardButton(opt, callback_data=f"ans_{i}")]
        for i, opt in enumerate(q["options"])
    ]

    query.message.reply_text(f"❓ {q['question']}", reply_markup=InlineKeyboardMarkup(keyboard))

# 🔥 BROADCAST
def broadcast(update, context):
    if update.effective_user.id != OWNER_ID:
        return

    msg = " ".join(context.args)
    if not msg:
        update.message.reply_text("Masukkan pesan!")
        return

    success = 0
    for chat_id in chat_list:
        try:
            context.bot.send_message(chat_id=int(chat_id), text=msg)
            success += 1
        except:
            pass

    update.message.reply_text(f"✅ Broadcast terkirim ke {success} chat")

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("broadcast", broadcast))
dp.add_handler(CallbackQueryHandler(button))

updater.start_polling()
updater.idle()
