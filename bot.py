import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

TOKEN = os.getenv("TOKEN")

questions = [
    {
        "question": "Hero dengan lifesteal tinggi?",
        "options": ["Alucard", "Layla", "Miya", "Eudora"],
        "answer": 0
    }
]

user_data = {}

def start(update, context):
    keyboard = [[InlineKeyboardButton("🔥 Mulai Quiz", callback_data="start")]]
    update.message.reply_text("🎮 Quiz MLBB!", reply_markup=InlineKeyboardMarkup(keyboard))

def button(update, context):
    query = update.callback_query
    query.answer()

    chat_id = query.message.chat.id

    if query.data == "start":
        user_data[chat_id] = {"index": 0, "score": 0}
        send_question(query)

    elif query.data.startswith("ans_"):
        ans = int(query.data.split("_")[1])
        user = user_data[chat_id]
        q = questions[user["index"]]

        if ans == q["answer"]:
            user["score"] += 1
            query.message.reply_text("✅ Benar!")
        else:
            query.message.reply_text("❌ Salah!")

        user["index"] += 1

        if user["index"] < len(questions):
            send_question(query)
        else:
            query.message.reply_text(f"🏆 Skor: {user['score']}")

def send_question(query):
    chat_id = query.message.chat.id
    user = user_data[chat_id]
    q = questions[user["index"]]

    keyboard = [
        [InlineKeyboardButton(opt, callback_data=f"ans_{i}")]
        for i, opt in enumerate(q["options"])
    ]

    query.message.reply_text(q["question"], reply_markup=InlineKeyboardMarkup(keyboard))

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CallbackQueryHandler(button))

updater.start_polling()
updater.idle()
