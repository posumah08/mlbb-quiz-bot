def get_rank(mmr):
    if mmr <= 2000:
        return "EPIC"
    elif mmr <= 5000:
        return "LEGEND"
    elif mmr <= 7500:
        return "<b>MYTHIC</b>"
    elif mmr <= 10000:
        return "<b>💫 MYTHIC HONOR 💫</b>"
    elif mmr <= 15000:
        return "<b>⭐️ MYTHIC GLORY ⭐️</b>"
    else:
        return "<b>🌟 MYTHIC IMMORTAL 🌟</b>"
