from achievement import ACHIEVEMENTS, format_achievement
import database

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
        }
    return user_progress[user_id]


def check_achievement(user_id, name, context, chat_id, q_type, answer):
    progress = get_user_progress(user_id)

    progress["streak"] += 1
    progress["total_correct"] += 1

    if q_type == "spell":
        progress["spell_correct"].add(answer)
    elif q_type == "item":
        progress["item_correct"].add(answer)
    elif q_type == "hero":
        progress["hero_correct"].add(answer)
    elif q_type == "emblem":
        progress["emblem_correct"].add(answer)

    unlocked_now = set()

    def unlock(key):
        if database.has_achievement(user_id, key):
            return

        database.add_achievement(user_id, key)
        unlocked_now.add(key)

        reward = ACHIEVEMENTS[key]["reward"]
        database.add_global_score(user_id, name, reward)

        text = format_achievement(name, key)

        context.bot.send_message(
            chat_id=int(chat_id),
            text=text,
            parse_mode="HTML"
        )

    # ================= CATEGORY =================
    from question_spell import QUESTIONS as SPELL_QUESTIONS
    from question_item import QUESTIONS as ITEM_QUESTIONS
    from question_hero import QUESTIONS as HERO_QUESTIONS
    from question_emblem import QUESTIONS as EMBLEM_QUESTIONS

    if len(progress["spell_correct"]) >= len(SPELL_QUESTIONS):
        unlock("spell_master")

    if len(progress["item_correct"]) >= len(ITEM_QUESTIONS):
        unlock("item_master")

    if len(progress["hero_correct"]) >= len(HERO_QUESTIONS):
        unlock("hero_master")

    if len(progress["emblem_correct"]) >= len(EMBLEM_QUESTIONS):
        unlock("emblem_master")

    # ================= STREAK =================
    streak = progress["streak"]

    if streak >= 10: unlock("streak_10")
    if streak >= 50: unlock("streak_50")
    if streak >= 100: unlock("streak_100")
    if streak >= 150: unlock("streak_150")
    if streak >= 200: unlock("streak_200")
    if streak >= 250: unlock("streak_250")

    # ================= MMR =================
    score = database.get_user_score(user_id)

    if score >= 50000: unlock("mmr_50k")
    if score >= 100000: unlock("mmr_100k")
    if score >= 250000: unlock("mmr_250k")
    if score >= 500000: unlock("mmr_500k")

    # ================= FINAL =================
    user_keys = set(database.get_user_achievements(user_id)) | unlocked_now
    all_keys = set(ACHIEVEMENTS.keys()) - {"all_complete"}

    if all_keys.issubset(user_keys):
        unlock("all_complete")


def reset_streak(user_id):
    progress = get_user_progress(user_id)
    progress["streak"] = 0
