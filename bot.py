from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

TOKEN = os.getenv(8719841221:AAHKSZ9DZW79iLXVzGPZdBYMGOTqZnPgzRo)

questions = [
    {
        "question": "Hero dengan julukan King of Lifesteal?",
        "options": ["Alucard", "Zilong", "Aldous", "Leomord"],
        "answer": 0
    },
    {
        "question": "Ultimate Harith bernama?",
        "options": ["Chrono Dash", "Zaman Force", "Black Shoes", "Time Rift"],
        "answer": 2
    }
]

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🔥 Mulai Quiz", callback_data="start")]]
    await update.message.reply_text("🎮 Selamat datang di Quiz MLBB!", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat.id

    if query.data == "start":
        user_data[chat_id] = {"index": 0, "score": 0}
        await send_question(query)

    elif query.data.startswith("ans_"):
        ans = int(query.data.split("_")[1])
        user = user_data[chat_id]
        q = questions[user["index"]]

        if ans == q["answer"]:
            user["score"] += 1
            await query.message.reply_text("✅ Benar!")
        else:
            await query.message.reply_text("❌ Salah!")

        user["index"] += 1

        if user["index"] < len(questions):
            await send_question(query)
        else:
            await query.message.reply_text(f"🏆 Quiz selesai!\nSkor kamu: {user['score']}/{len(questions)}")

async def send_question(query):
    chat_id = query.message.chat.id
    user = user_data[chat_id]
    q = questions[user["index"]]

    keyboard = [
        [InlineKeyboardButton(opt, callback_data=f"ans_{i}")]
        for i, opt in enumerate(q["options"])
    ]

    await query.message.reply_text(
        f"❓ {q['question']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
