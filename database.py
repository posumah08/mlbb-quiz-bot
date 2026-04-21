import sqlite3

conn = sqlite3.connect("data.db", check_same_thread=False)
c = conn.cursor()

# tabel leaderboard
c.execute("""
CREATE TABLE IF NOT EXISTS leaderboard (
    chat_id TEXT,
    name TEXT,
    score INTEGER
)
""")

# tabel chat
c.execute("""
CREATE TABLE IF NOT EXISTS chats (
    chat_id TEXT
)
""")

conn.commit()

def save_chat(chat_id):
    c.execute("INSERT OR IGNORE INTO chats VALUES (?)", (chat_id,))
    conn.commit()

def get_chats():
    return [row[0] for row in c.execute("SELECT chat_id FROM chats")]

def save_score(chat_id, name, score):
    c.execute("DELETE FROM leaderboard WHERE chat_id=?", (chat_id,))
    c.execute("INSERT INTO leaderboard VALUES (?, ?, ?)", (chat_id, name, score))
    conn.commit()

def get_leaderboard():
    return c.execute("SELECT name, score FROM leaderboard ORDER BY score DESC LIMIT 10").fetchall()