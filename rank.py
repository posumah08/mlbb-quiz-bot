def get_rank(mmr):
    if mmr <= 2000:
        return "EPIC"
    elif mmr <= 4000:
        return "LEGEND"
    elif mmr <= 10000:
        return "HONOR"
    else:
        return "IMMORTAL"
