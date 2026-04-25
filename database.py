import psycopg2
import os

# ================= CONFIG =================

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL tidak ditemukan! Pastikan sudah set di Railway Variables")

# ================= CONNECT =================

def get_conn():
    return psycopg2.connect(DATABASE_URL)

# ================= INIT =================

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    try:
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
    finally:
        cur.close()
        conn.close()

# ================= GLOBAL =================

def add_global_score(user_id, name, points):
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
        INSERT INTO global_scores (user_id, name, score)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id)
        DO UPDATE SET score = global_scores.score + %s
        """, (user_id, name, points, points))

        conn.commit()
    finally:
        cur.close()
        conn.close()

def get_user_score(user_id):
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("SELECT score FROM global_scores WHERE user_id = %s", (user_id,))
        result = cur.fetchone()
        return result[0] if result else 0
    finally:
        cur.close()
        conn.close()

def get_global_leaderboard(limit=15):
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
        SELECT name, score FROM global_scores
        ORDER BY score DESC
        LIMIT %s
        """, (limit,))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

# ================= GLOBAL RANK =================

def get_global_rank(user_id):
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
        SELECT rank FROM (
            SELECT user_id,
                   RANK() OVER (ORDER BY score DESC) as rank
            FROM global_scores
        ) ranked
        WHERE user_id = %s
        """, (user_id,))
        
        result = cur.fetchone()
        return result[0] if result else None
    finally:
        cur.close()
        conn.close()

# ================= GROUP =================

def add_group_score(chat_id, user_id, name, points):
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
        INSERT INTO group_scores (chat_id, user_id, name, score)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (chat_id, user_id)
        DO UPDATE SET score = group_scores.score + %s
        """, (chat_id, user_id, name, points, points))

        conn.commit()
    finally:
        cur.close()
        conn.close()

def get_group_leaderboard(chat_id, limit=20):
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
        SELECT name, score FROM group_scores
        WHERE chat_id = %s
        ORDER BY score DESC
        LIMIT %s
        """, (chat_id, limit))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()
