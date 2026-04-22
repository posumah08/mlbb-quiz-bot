import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

def init_db():
    cur.execute("""
    CREATE TABLE IF NOT EXISTS global_scores (
        user_id TEXT PRIMARY KEY,
        name TEXT,
        score INT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS group_scores (
        chat_id TEXT,
        user_id TEXT,
        name TEXT,
        score INT,
        PRIMARY KEY (chat_id, user_id)
    )
    """)

    conn.commit()

# ================= GLOBAL =================

def add_global_score(user_id, name, points):
    cur.execute("""
    INSERT INTO global_scores (user_id, name, score)
    VALUES (%s, %s, %s)
    ON CONFLICT (user_id)
    DO UPDATE SET score = global_scores.score + %s
    """, (user_id, name, points, points))
    conn.commit()

def get_user_score(user_id):
    cur.execute("SELECT score FROM global_scores WHERE user_id = %s", (user_id,))
    result = cur.fetchone()
    return result[0] if result else 0

def get_global_leaderboard(limit=10):
    cur.execute("""
    SELECT name, score FROM global_scores
    ORDER BY score DESC
    LIMIT %s
    """, (limit,))
    return cur.fetchall()

# ================= GROUP =================

def add_group_score(chat_id, user_id, name, points):
    cur.execute("""
    INSERT INTO group_scores (chat_id, user_id, name, score)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (chat_id, user_id)
    DO UPDATE SET score = group_scores.score + %s
    """, (chat_id, user_id, name, points, points))
    conn.commit()

def get_group_leaderboard(chat_id, limit=10):
    cur.execute("""
    SELECT name, score FROM group_scores
    WHERE chat_id = %s
    ORDER BY score DESC
    LIMIT %s
    """, (chat_id, limit))
    return cur.fetchall()
