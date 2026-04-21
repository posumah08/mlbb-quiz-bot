import random

QUESTIONS = [
    {"question": "Hero lifesteal tinggi?", "options": ["Alucard","Layla","Miya","Eudora"], "answer": 0},
    {"question": "Ultimate Harith?", "options": ["Chrono Dash","Zaman Force","Black Shoes","Time Rift"], "answer": 2}
]

def get_questions():
    return random.sample(QUESTIONS, len(QUESTIONS))