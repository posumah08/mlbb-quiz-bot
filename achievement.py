ACHIEVEMENTS = {

    "spell_master": {
        "name": "<b>🧿 Raja Spell</b>",
        "desc": "Jawab semua Spell",
        "reward": 500
    },
    "item_master": {
        "name": "<b>🛡️ Master Item</b>",
        "desc": "Jawab semua Item",
        "reward": 500
    },
    "emblem_master": {
        "name": "<b>🎯 Ahli Emblem</b>",
        "desc": "Jawab semua Emblem",
        "reward": 500
    },
    "hero_master": {
        "name": "<b>⚔️ Master Hero</b>",
        "desc": "Jawab semua Hero",
        "reward": 500
    },
    "ultimate_master": {
        "name": "<b>💥 Penguasa Ultimate</b>",
        "desc": "Jawab semua Ultimate",
        "reward": 500
    },

    "streak_10": {"name": "<b>🔥 On Fire</b>", "desc": "10x benar", "reward": 500},
    "streak_50": {"name": "<b>⚡ Gak Ketahan</b>", "desc": "50x benar", "reward": 500},
    "streak_100": {"name": "<b>🧠 Dewa Jawaban</b>", "desc": "100x benar", "reward": 500},
    "streak_150": {"name": "<b>👁️ Otak Dewa</b>", "desc": "150x benar", "reward": 500},
    "streak_200": {"name": "<b>♾️ Immortal</b>", "desc": "200x benar", "reward": 500},
    "streak_250": {"name": "<b>👶 Anak Moonton</b>", "desc": "250x benar", "reward": 500},

    "mmr_50k": {"name": "<b>💸 Idol 50K</b>", "desc": "50K MMR", "reward": 500},
    "mmr_100k": {"name": "<b>💎 No Life 100K</b>", "desc": "100K MMR", "reward": 500},
    "mmr_250k": {"name": "<b>⚔️ Dewa Perang 250K</b>", "desc": "250K MMR", "reward": 500},
    "mmr_500k": {"name": "<b>👑 Real No Life 500K</b>", "desc": "500K MMR", "reward": 500},

    "active_3": {"name": "<b>🌱 Mulai Rajin</b>", "desc": "3 hari", "reward": 500},
    "active_7": {"name": "<b>📈 Konsisten</b>", "desc": "7 hari", "reward": 500},
    "active_10": {"name": "<b>🎮 Niat Main</b>", "desc": "10 hari", "reward": 500},
    "active_30": {"name": "<b>🏆 MASTER MLBB</b>", "desc": "30 hari", "reward": 500},

    "all_complete": {
        "name": "<b>🌟 Sang Legenda</b>",
        "desc": "Semua achievement",
        "reward": 500
    }
}

# ================= FORMAT NOTIF =================

def format_achievement(name, achievement_key):
    data = ACHIEVEMENTS.get(achievement_key)

    if not data:
        return None

    return (
        f"🏆 Achievement Terbuka!\n\n"
        f"{data['name']}\n"
        f"User : {name}\n\n"
        f"{data['desc']} berhasil kamu selesaikan.\n\n"
        f"+{data['reward']} MMR\n\n"
        f"/achieve untuk lihat semua pencapaian"
    )
