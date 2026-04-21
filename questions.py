import random

QUESTIONS = [
    {"question": "Hero lifesteal tinggi?", "options": ["Alucard","Layla","Miya","Eudora"], "answer": 0},
    {"question": "Ultimate Harith?", "options": ["Chrono Dash","Zaman Force","Black Shoes","Time Rift"], "answer": 2},
    {"question": "Hero tank MLBB?", "options": ["Tigreal","Layla","Gusion","Fanny"], "answer": 0},
    {"question": "Hero assassin?", "options": ["Miya","Saber","Estes","Franco"], "answer": 1},
    {"question": "Hero support healer?", "options": ["Estes","Zilong","Chou","Ling"], "answer": 0},
    {"question": "Hero dengan hook?", "options": ["Franco","Balmond","Miya","Lylia"], "answer": 0},
    {"question": "Hero ninja MLBB?", "options": ["Hayabusa","Layla","Aurora","Hilda"], "answer": 0},
    {"question": "Hero marksman awal MLBB?", "options": ["Layla","Fanny","Aldous","Gusion"], "answer": 0},
    {"question": "Hero mage burst?", "options": ["Eudora","Alucard","Bane","Sun"], "answer": 0},
    {"question": "Hero split push?", "options": ["Sun","Angela","Rafaela","Kaja"], "answer": 0},

    {"question": "Hero dengan skill kabel?", "options": ["Fanny","Layla","Grock","Bruno"], "answer": 0},
    {"question": "Hero tank dengan shield besar?", "options": ["Uranus","Miya","Clint","Zilong"], "answer": 0},
    {"question": "Hero ulti global heal?", "options": ["Estes","Aamon","Lancelot","Karina"], "answer": 0},
    {"question": "Hero combo cepat?", "options": ["Gusion","Balmond","Layla","Franco"], "answer": 0},
    {"question": "Hero dengan trap?", "options": ["Popol","Bruno","Alpha","Minotaur"], "answer": 0},
    {"question": "Hero ulti lompat ke belakang?", "options": ["Chou","Layla","Miya","Aurora"], "answer": 0},
    {"question": "Hero mage ice?", "options": ["Aurora","Bane","Gusion","Roger"], "answer": 0},
    {"question": "Hero dengan summon bayangan?", "options": ["Sun","Layla","Karrie","Hanabi"], "answer": 0},
    {"question": "Hero dengan ulti besar di area?", "options": ["Pharsa","Zilong","Chou","Saber"], "answer": 0},
    {"question": "Hero tank banteng?", "options": ["Minotaur","Layla","Fanny","Ling"], "answer": 0},

    {"question": "Hero assassin lari cepat?", "options": ["Ling","Miya","Eudora","Franco"], "answer": 0},
    {"question": "Hero mage kecil lompat?", "options": ["Lylia","Balmond","Chou","Roger"], "answer": 0},
    {"question": "Hero fighter spin?", "options": ["Balmond","Layla","Gusion","Angela"], "answer": 0},
    {"question": "Hero dengan skill charge?", "options": ["Hilda","Miya","Clint","Valir"], "answer": 0},
    {"question": "Hero dengan turret skill?", "options": ["Zhask","Layla","Chou","Bruno"], "answer": 0},
    {"question": "Hero support speed boost?", "options": ["Rafaela","Zilong","Aldous","Karina"], "answer": 0},
    {"question": "Hero mage api?", "options": ["Valir","Aurora","Sun","Grock"], "answer": 0},
    {"question": "Hero tank batu?", "options": ["Grock","Layla","Miya","Lancelot"], "answer": 0},
    {"question": "Hero assassin dash banyak?", "options": ["Lancelot","Franco","Bane","Clint"], "answer": 0},
    {"question": "Hero ulti 1 pukulan?", "options": ["Aldous","Layla","Miya","Kagura"], "answer": 0},

    {"question": "Hero mage payung?", "options": ["Kagura","Zilong","Bruno","Sun"], "answer": 0},
    {"question": "Hero dengan skill lempar bola?", "options": ["Bruno","Layla","Ling","Chou"], "answer": 0},
    {"question": "Hero fighter dengan shield besar?", "options": ["Thamuz","Layla","Gusion","Angela"], "answer": 0},
    {"question": "Hero dengan ulti global link?", "options": ["Angela","Chou","Balmond","Fanny"], "answer": 0},
    {"question": "Hero dengan skill invis?", "options": ["Natalia","Layla","Miya","Balmond"], "answer": 0},
    {"question": "Hero assassin magic?", "options": ["Karina","Layla","Bruno","Clint"], "answer": 0},
    {"question": "Hero marksman dengan shield?", "options": ["Hanabi","Zilong","Chou","Grock"], "answer": 0},
    {"question": "Hero dengan skill tarik banyak?", "options": ["Atlas","Layla","Miya","Roger"], "answer": 0},
    {"question": "Hero fighter api?", "options": ["X.Borg","Layla","Miya","Aurora"], "answer": 0},
    {"question": "Hero mage lightning?", "options": ["Eudora","Sun","Franco","Hilda"], "answer": 0},

    {"question": "Hero assassin burst tinggi?", "options": ["Gusion","Layla","Miya","Angela"], "answer": 0},
    {"question": "Hero dengan pet serigala?", "options": ["Popol","Layla","Chou","Zilong"], "answer": 0},
    {"question": "Hero tank dengan heal terus?", "options": ["Uranus","Layla","Bruno","Sun"], "answer": 0},
    {"question": "Hero mage dengan ulti petir area?", "options": ["Eudora","Aurora","Kagura","Valir"], "answer": 0},
    {"question": "Hero fighter tombak?", "options": ["Zilong","Layla","Gusion","Angela"], "answer": 0},
    {"question": "Hero assassin lompat tembok?", "options": ["Ling","Layla","Miya","Franco"], "answer": 0},
    {"question": "Hero mage ultimate hujan meteor?", "options": ["Vale","Layla","Chou","Grock"], "answer": 0},
    {"question": "Hero support heal + speed?", "options": ["Rafaela","Sun","Zilong","Ling"], "answer": 0},
    {"question": "Hero fighter dengan lifesteal besar?", "options": ["Alucard","Layla","Miya","Aurora"], "answer": 0},
    {"question": "Hero dengan ulti serangan global?", "options": ["Aldous","Layla","Chou","Franco"], "answer": 0},

    # Tambahan hingga 100 (variasi)
]

# Auto nambah sampai 100 soal
while len(QUESTIONS) < 100:
    QUESTIONS.append(random.choice(QUESTIONS))

def get_questions():
    return random.sample(QUESTIONS, len(QUESTIONS))
