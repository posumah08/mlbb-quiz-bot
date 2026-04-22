def get_rank(mmr):
    if mmr <= 2000:
        return "EPIC"
    elif mmr <= 4000:
        return "LEGEND"
    elif mmr <= 10000:
        return "HONOR"
    else:
        return "IMMORTAL"


def get_rank_emoji(rank):
    if rank == "EPIC":
        return "<tg-emoji emoji-id='5436186359050030684'></tg-emoji>"
    elif rank == "LEGEND":
        return "<tg-emoji emoji-id='5436072593956294076'></tg-emoji>"
    elif rank == "HONOR":
        return "<tg-emoji emoji-id='5440505811954587601'></tg-emoji>"
    else:
        return "<tg-emoji emoji-id='5434039403683009050'></tg-emoji>"
