def get_rank(mmr):
    if mmr <= 2000:
        return "EPIC"
    elif mmr <= 5000:
        return "LEGEND"
    elif mmr <= 7500:
        return "MYTHIC"
    elif mmr <= 10000:
        return "MYTHIC HONOR"
    elif mmr <= 15000:
        return "MYTHIC GLORY"
    else:
        return "IMMORTAL"
