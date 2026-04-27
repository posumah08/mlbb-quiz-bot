from achievement import ACHIEVEMENTS, format_achievement
import database

# ================= TRACKING =================

# Simpan progress sementara (memory)
user_progress = {}

def get_user_progress(user_id):
    if user_id not in user_progress:
        user_progress[user_id] = {
            "streak": 0,
            "total_correct": 0,
            "spell_correct": set(),
            "item_correct": set(),
            "hero_correct": set(),
            "emblem_correct": set(),
            "active_days": set()
        }
    return user_progress[user_id]

# ================= CHECK ACHIEVEMENT =================

def check_achievement(user_id, name, context, chat_id, q_type, answer):
    progress = get_user_progress(user_id)

    # ================= UPDATE DATA =================

    progress["streak"] += 1
    progress["total_correct"] += 1

    # tracking per kategori
    if q_type == "spell":
        progress["spell_correct"].add(answer)
    elif q_type == "item":
        progress["item_correct"].add(answer)
    elif q_type == "hero":
        progress["hero_correct"].add(answer)
    elif q_type == "emblem":
        progress["emblem_correct"].add(answer)

    # ================= CHECK FUNCTIONS =================

    def unlock(key):
        if database.has_achievement(user_id, key):
            return

        database.add_achievement(user_id, key)

        reward = ACHIEVEMENTS[key]["reward"]
        database.add_global_score(user_id, name, reward)

        text = format_achievement(name, key)

        context.bot.send_message(
            chat_id=int(chat_id),
            text=text,
            parse_mode="HTML"
        )

    # ================= SPELL =================
    if len(progress["spell_correct"]) >= 13:  # jumlah spell MLBB
        unlock("spell_master")

    # ================= ITEM =================
    if len(progress["item_correct"]) >= 50:
        unlock("item_master")

    # ================= HERO =================
    if len(progress["hero_correct"]) >= 120:
        unlock("hero_master")

    # ================= EMBLEM =================
    if len(progress["emblem_correct"]) >= 20:
        unlock("emblem_master")

    # ================= STREAK =================
    streak = progress["streak"]

    if streak >= 10:
        unlock("streak_10")
    if streak >= 50:
        unlock("streak_50")
    if streak >= 100:
        unlock("streak_100")
    if streak >= 150:
        unlock("streak_150")
    if streak >= 200:
        unlock("streak_200")
    if streak >= 250:
        unlock("streak_250")

    # ================= MMR =================
    score = database.get_user_score(user_id)

    if score >= 50000:
        unlock("mmr_50k")
    if score >= 100000:
        unlock("mmr_100k")
    if score >= 250000:
        unlock("mmr_250k")
    if score >= 500000:
        unlock("mmr_500k")

    # ================= FINAL =================
    all_keys = set(ACHIEVEMENTS.keys())
    user_keys = set(database.get_user_achievements(user_id))

    if all_keys.issubset(user_keys):
        unlock("all_complete")


# ================= RESET STREAK =================

def reset_streak(user_id):
    progress = get_user_progress(user_id)
    progress["streak"] = 0
