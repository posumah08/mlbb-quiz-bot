from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import TOKEN
from question_hero import QUESTIONS as HERO_QUESTIONS
from question_spell import QUESTIONS as SPELL_QUESTIONS
from question_item import QUESTIONS as ITEM_QUESTIONS
from question_emblem import QUESTIONS as EMBLEM_QUESTIONS
from rank import get_rank
from achievement_handler import check_achievement, reset_streak
from achievement import ACHIEVEMENTS  # 🔥 TAMBAHAN
import database
import random
import os

user_data = {}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OWNER_ID = "6776834334"

# ================= POLA ==================
PATTERN = [
    "hero","hero","item",
    "hero","hero","item",
    "hero","hero","item",
    "emblem",
    "hero","hero","item",
    "hero","hero","item",
    "spell"
]

# ================= UTIL ==================

def group_only(update):
    return update.effective_chat.type in ["group", "supergroup"]

def send_next_question(context):
    chat_id = context.job.context
    send_question(context.bot, chat_id)

def get_from_pool(user, key):
    pool_key = f"{key}_pool"
    index_key = f"{key}_index"
    data_key = f"{key}_data"

    pool = user[pool_key]
    idx = user[index_key]

    if idx >= len(pool):
        pool = random.sample(user[data_key], len(user[data_key]))
        user[pool_key] = pool
        user[index_key] = 0
        idx = 0

    q = pool[idx]
    user[index_key] += 1
    return q

# ================= START ==================

def start(update, context):
    if update.effective_chat.type == "private":

        keyboard = [
            [InlineKeyboardButton("Dev", url="https://t.me/yasanyamagurai")],
            [InlineKeyboardButton("Tambahkan ke GRUP", url="https://t.me/quizmlbb_bot?startgroup=true")]
        ]

        update.message.reply_text(
            "Halo Player, Selamat bergabung di\n"
            "QUIZ MLBB ID.\n"
            "Tambahkan Bot ini di GRUP TELEGRAM untuk Mulai Permainan.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if not group_only(update):
        return

    chat_id = str(update.effective_chat.id)

    if chat_id in user_data and user_data[chat_id].get("active"):
        update.message.reply_text("Game masih berjalan!")
        return

    user_data[chat_id] = {
        "active": True,
        "pattern_index": random.randint(0, len(PATTERN)-1),

        "hero_data": HERO_QUESTIONS,
        "item_data": ITEM_QUESTIONS,
        "spell_data": SPELL_QUESTIONS,
        "emblem_data": EMBLEM_QUESTIONS,

        "hero_pool": random.sample(HERO_QUESTIONS, len(HERO_QUESTIONS)),
        "item_pool": random.sample(ITEM_QUESTIONS, len(ITEM_QUESTIONS)),
        "spell_pool": random.sample(SPELL_QUESTIONS, len(SPELL_QUESTIONS)),
        "emblem_pool": random.sample(EMBLEM_QUESTIONS, len(EMBLEM_QUESTIONS)),

        "hero_index": 0,
        "item_index": 0,
        "spell_index": 0,
        "emblem_index": 0,

        "current_q": None,
        "last_q_msg": None,
        "answered": False,
        "current_type": None
    }

    send_question(context.bot, chat_id)

# ================= GAME ==================

def send_question(bot, chat_id):
    if chat_id not in user_data:
        return

    user = user_data[chat_id]

    q_type = PATTERN[user["pattern_index"]]
    user["pattern_index"] = (user["pattern_index"] + 1) % len(PATTERN)

    if q_type == "hero":
        q = get_from_pool(user, "hero")
    elif q_type == "item":
        q = get_from_pool(user, "item")
    elif q_type == "spell":
        q = get_from_pool(user, "spell")
    else:
        q = get_from_pool(user, "emblem")

    user["current_q"] = q
    user["answered"] = False
    user["current_type"] = q_type

    image_path = os.path.join(BASE_DIR, *q["image"].split("/"))

    caption_map = {
        "hero": "❓ Tebak hero ini!",
        "item": "❓ Tebak item ini!",
        "spell": "❓ Tebak spell ini!",
        "emblem": "❓ Tebak talent/emblem ini!"
    }

    if not os.path.exists(image_path):
        bot.send_message(chat_id=int(chat_id), text="Gambar tidak ditemukan!")
        return

    try:
        with open(image_path, "rb") as img:
            msg = bot.send_photo(
                chat_id=int(chat_id),
                photo=img,
                caption=caption_map[q_type]
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

    if not user.get("active") or user.get("answered"):
        return

    if update.message.reply_to_message:
        if update.message.reply_to_message.message_id != user.get("last_q_msg"):
            return

    q = user.get("current_q")
    if not q:
        return

    correct = q["answer"].lower()
    aliases = q.get("aliases", [])

    valid_answers = [correct] + aliases

    user_input = text.replace(" ", "")
    valid_answers = [ans.lower().replace(" ", "") for ans in valid_answers]

    if user_input in valid_answers:
        user["answered"] = True

        try:
            database.add_global_score(user_id, name, 25)
            database.add_group_score(chat_id, user_id, name, 25)
        except:
            pass

        # 🔥 ACHIEVEMENT AUTO
        check_achievement(
            user_id=user_id,
            name=name,
            context=context,
            chat_id=chat_id,
            q_type=user.get("current_type"),
            answer=correct
        )

        score = database.get_user_score(user_id) or 0
        rank_name = get_rank(score)

        context.bot.send_message(
            chat_id=int(chat_id),
            text=(
                f"🎉 {display_name} menjawab dengan benar!\n\n"
                f"🔥 +25 MMR\n"
                f"📊 TOTAL MMR: {score}\n"
                f"🏆 RANK: {rank_name}"
            ),
            parse_mode="HTML"
        )

        try:
            last = user.get("last_q_msg")
            if last:
                context.bot.delete_message(chat_id=int(chat_id), message_id=last)
        except:
            pass

        context.job_queue.run_once(send_next_question, 3, context=chat_id)

    else:
        reset_streak(user_id)

# ================= ACHIEVE ==================

def achieve(update, context):
    user_id = str(update.effective_user.id)
    data = database.get_user_achievements(user_id)

    if not data:
        update.message.reply_text("Kamu belum punya achievement 😢")
        return

    text = "🏆 Achievement Kamu:\n\n"

    for key in data:
        ach = ACHIEVEMENTS.get(key)
        if ach:
            text += f"{ach['name']}\n"

    update.message.reply_text(text, parse_mode="HTML")

# ================= NEXT ==================

def next_q(update, context):
    if not group_only(update):
        return

    chat_id = str(update.effective_chat.id)

    if chat_id not in user_data or not user_data[chat_id].get("active"):
        update.message.reply_text("⚠️ Game belum dimulai!")
        return

    user = user_data[chat_id]

    if not user.get("answered") and user.get("current_q"):
        q = user["current_q"]
        ans = q["answer"]
        aliases = q.get("aliases", [])

        if aliases:
            text = f"💡 Jawaban: {ans.title()} ({aliases[0]})"
        else:
            text = f"💡 Jawaban: {ans.title()}"

        context.bot.send_message(chat_id=int(chat_id), text=text)

    try:
        last = user.get("last_q_msg")
        if last:
            context.bot.delete_message(chat_id=int(chat_id), message_id=last)
    except:
        pass

    send_question(context.bot, chat_id)

# ================= LEADERBOARD ==================

def leaderboard(update, context):
    data = database.get_global_leaderboard()

    if not data:
        update.message.reply_text("Belum ada data leaderboard.")
        return

    text = "🏆 LEADERBOARD GLOBAL 🏆\n\n"

    for i, (name, score) in enumerate(data, start=1):
        rank_name = get_rank(score)
        text += f"{i}. {name} — {rank_name} ({score})\n"

    update.message.reply_text(text)

# ================= TOP GRUP ==================

def topgrup(update, context):
    chat_id = str(update.effective_chat.id)
    data = database.get_group_leaderboard(chat_id)

    if not data:
        update.message.reply_text("Belum ada leaderboard di grup ini.")
        return

    text = "🏆 LEADERBOARD GRUP 🏆\n\n"

    for i, (name, score) in enumerate(data, start=1):
        rank_name = get_rank(score)
        text += f"{i}. {name} — {rank_name} ({score})\n"

    update.message.reply_text(text)

# ================= STATS ==================

def stats(update, context):
    user_id = str(update.effective_user.id)

    score = database.get_user_score(user_id) or 0
    rank_name = get_rank(score)
    global_rank = database.get_global_rank(user_id)

    update.message.reply_text(
        f"📊 Stats\n\n"
        f"🔥 MMR: {score}\n"
        f"🏆 Rank: {rank_name}\n"
        f"🌍 Global Rank: #{global_rank if global_rank else '-'}"
    )

# ================= RUN ==================

def main():
    database.init_db()

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("next", next_q))
    dp.add_handler(CommandHandler("leaderboard", leaderboard))
    dp.add_handler(CommandHandler("topgrup", topgrup))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("achieve", achieve))  # 🔥 TAMBAHAN
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, answer))

    print("BOT RUNNING...")

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
