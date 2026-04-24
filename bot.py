from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import TOKEN
from question_hero import QUESTIONS as HERO_QUESTIONS
from question_spell import QUESTIONS as SPELL_QUESTIONS
from question_item import QUESTIONS as ITEM_QUESTIONS
from rank import get_rank
import database
import random
import os

user_data = {}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ================= UTIL ==================

def valid_command(text):
    if not text:
        return True
    text = text.lower()
    return not ("@" in text and "@quizmlbb_bot" not in text)

def group_only(update):
    return update.effective_chat.type in ["group", "supergroup"]

def send_next_question(context):
    chat_id = context.job.context
    send_question(context.bot, chat_id)

# ================= START ==================

def start(update, context):
    if update.effective_chat.type == "private":

        keyboard = [
            [InlineKeyboardButton("Dev", url="https://t.me/yasanyamagurai")],
            [InlineKeyboardButton("Tambahkan ke GRUP", url="https://t.me/quizmlbb_bot?startgroup=true")]
        ]

        update.message.reply_text(
            "Halo Player, Selamat bergabung di QUIZ MLBB ID.\n"
            "Tambahkan Bot ini di GRUP TELEGRAM untuk Mulai Permainan.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if not group_only(update):
        return

    chat_id = str(update.effective_chat.id)
    text = update.message.text

    if not valid_command(text):
        return

    if chat_id in user_data and user_data[chat_id].get("active"):
        update.message.reply_text("Game masih berjalan!")
        return

    # 🔥 gabung semua soal
    all_questions = HERO_QUESTIONS + SPELL_QUESTIONS + ITEM_QUESTIONS

    user_data[chat_id] = {
        "active": True,
        "questions": random.sample(all_questions, len(all_questions)),
        "index": 0,
        "current_q": None,
        "last_q_msg": None,
        "answered": False
    }

    send_question(context.bot, chat_id)

# ================= GAME ==================

def send_question(bot, chat_id):
    if chat_id not in user_data:
        return

    user = user_data[chat_id]

    if user["index"] >= len(user["questions"]):
        all_questions = HERO_QUESTIONS + SPELL_QUESTIONS + ITEM_QUESTIONS
        user["questions"] = random.sample(all_questions, len(all_questions))
        user["index"] = 0

    q = user["questions"][user["index"]]
    user["index"] += 1

    user["current_q"] = q
    user["answered"] = False

    image_path = os.path.join(BASE_DIR, *q["image"].split("/"))

    print("=== DEBUG GAMBAR ===")
    print("Soal:", q)
    print("Path:", image_path)
    print("Ada file?", os.path.exists(image_path))
    print("====================")

    # 🔥 caption otomatis
    if "spell" in q["image"].lower():
        caption = "❓ Tebak spell ini!"
    elif "item" in q["image"].lower():
        caption = "❓ Tebak item ini!"
    else:
        caption = "❓ Tebak hero ini!"

    if not os.path.exists(image_path):
        print("❌ Gambar tidak ditemukan:", image_path)
        bot.send_message(chat_id=int(chat_id), text="Gambar tidak ditemukan!")
        return

    try:
        with open(image_path, "rb") as img:
            msg = bot.send_photo(
                chat_id=int(chat_id),
                photo=img,
                caption=caption
            )

        user["last_q_msg"] = msg.message_id

    except Exception as e:
        print("ERROR GAMBAR:", image_path, e)
        bot.send_message(chat_id=int(chat_id), text="Gagal kirim gambar!")

# ================= JAWAB ==================

def answer(update, context):
    if not group_only(update):
        return

    if not update.message or not update.message.text:
        return

    chat_id = str(update.effective_chat.id)
    user_id = str(update.effective_user.id)

    name = update.effective_user.first_name
    username = update.effective_user.username
    display_name = f"@{username}" if username else name

    text = update.message.text.lower().strip()

    if chat_id not in user_data:
        return

    user = user_data[chat_id]

    if not user.get("active"):
        return

    if update.message.reply_to_message:
        if update.message.reply_to_message.message_id != user.get("last_q_msg"):
            return

    if user.get("answered"):
        return

    q = user.get("current_q")
    if not q:
        return

    correct = q["answer"].lower()

    if text.replace(" ", "") == correct.replace(" ", ""):
        user["answered"] = True

        try:
            database.add_global_score(user_id, name, 25)
            database.add_group_score(chat_id, user_id, name, 25)
        except Exception as e:
            print("DB ERROR:", e)

        score = database.get_user_score(user_id) or 0
        rank = get_rank(score)

        context.bot.send_message(
            chat_id=int(chat_id),
            text=(
                f"🎉 {display_name} menjawab dengan benar!\n\n"
                f"🔥 +25 MMR\n"
                f"📊 TOTAL MMR: {score}\n"
                f"🏆 RANK: {rank}"
            )
        )

        try:
            last = user.get("last_q_msg")
            if last:
                context.bot.delete_message(chat_id=int(chat_id), message_id=last)
        except:
            pass

        context.job_queue.run_once(send_next_question, 3, context=chat_id)

# ================= NEXT ==================

def next_q(update, context):
    if not group_only(update):
        return

    chat_id = str(update.effective_chat.id)
    text = update.message.text

    if not valid_command(text):
        return

    # 🔥 notif kalau belum mulai
    if chat_id not in user_data or not user_data[chat_id].get("active"):
        update.message.reply_text("⚠️ Game belum dimulai!")
        return

    user = user_data[chat_id]

    # 🔥 kasih jawaban kalau belum dijawab
    if not user.get("answered") and user.get("current_q"):
        answer = user["current_q"]["answer"]

        context.bot.send_message(
            chat_id=int(chat_id),
            text=f"💡 Jawaban: {answer.title()}"
        )

    # hapus soal lama
    try:
        last = user.get("last_q_msg")
        if last:
            context.bot.delete_message(chat_id=int(chat_id), message_id=last)
    except:
        pass

    send_question(context.bot, chat_id)

# ================= RUN ==================

def main():
    database.init_db()

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("next", next_q))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, answer))

    print("BOT RUNNING...")

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
