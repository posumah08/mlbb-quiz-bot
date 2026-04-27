import psycopg2
from psycopg2 import pool
import os

# ================= CONFIG =================

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL tidak ditemukan! Pastikan sudah set di Railway Variables")

# ================= POOL =================

db_pool = None

def init_pool():
    global db_pool
    if db_pool is not None:
        return

    try:
        db_pool = psycopg2.pool.SimpleConnectionPool(
            1, 10,
            DATABASE_URL,
            sslmode='require'
        )
        print("DB Pool Ready")
    except Exception as e:
        print("POOL ERROR:", e)
        raise e

def get_conn():
    global db_pool

    if db_pool is None:
        init_pool()  # 🔥 AUTO INIT (ini fix utama)

    try:
        return db_pool.getconn()
    except Exception as e:
        print("DB CONNECT ERROR:", e)
        raise e

def release_conn(conn):
    global db_pool
    try:
        if db_pool:
            db_pool.putconn(conn)
    except:
        pass

# ================= INIT =================

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    try:
        # GLOBAL SCORE
        cur.execute("""
        CREATE TABLE IF NOT EXISTS global_scores (
            user_id TEXT PRIMARY KEY,
            name TEXT,
            score INT DEFAULT 0
        )
        """)

        # GROUP SCORE
        cur.execute("""
        CREATE TABLE IF NOT EXISTS group_scores (
            chat_id TEXT,
            user_id TEXT,
            name TEXT,
            score INT DEFAULT 0,
            PRIMARY KEY (chat_id, user_id)
        )
        """)

        # ACHIEVEMENTS
        cur.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            user_id TEXT,
            achievement_key TEXT,
            PRIMARY KEY (user_id, achievement_key)
        )
        """)

        conn.commit()

    except Exception as e:
        print("INIT DB ERROR:", e)
        conn.rollback()

    finally:
        cur.close()
        release_conn(conn)

# ================= GLOBAL =================

def add_global_score(user_id, name, points):
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
        INSERT INTO global_scores (user_id, name, score)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id)
        DO UPDATE SET 
            score = global_scores.score + EXCLUDED.score,
            name = EXCLUDED.name
        """, (user_id, name, points))

        conn.commit()

    except Exception as e:
        print("ADD GLOBAL SCORE ERROR:", e)
        conn.rollback()

    finally:
        cur.close()
        release_conn(conn)

def get_user_score(user_id):
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("SELECT score FROM global_scores WHERE user_id = %s", (user_id,))
        result = cur.fetchone()
        return result[0] if result else 0

    except Exception as e:
        print("GET USER SCORE ERROR:", e)
        return 0

    finally:
        cur.close()
        release_conn(conn)

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

    except Exception as e:
        print("LEADERBOARD ERROR:", e)
        return []

    finally:
        cur.close()
        release_conn(conn)

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

    except Exception as e:
        print("GET RANK ERROR:", e)
        return None

    finally:
        cur.close()
        release_conn(conn)

# ================= GROUP =================

def add_group_score(chat_id, user_id, name, points):
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
        INSERT INTO group_scores (chat_id, user_id, name, score)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (chat_id, user_id)
        DO UPDATE SET 
            score = group_scores.score + EXCLUDED.score,
            name = EXCLUDED.name
        """, (chat_id, user_id, name, points))

        conn.commit()

    except Exception as e:
        print("ADD GROUP SCORE ERROR:", e)
        conn.rollback()

    finally:
        cur.close()
        release_conn(conn)

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

    except Exception as e:
        print("GROUP LEADERBOARD ERROR:", e)
        return []

    finally:
        cur.close()
        release_conn(conn)

# ================= ACHIEVEMENTS =================

def add_achievement(user_id, achievement_key):
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
        INSERT INTO achievements (user_id, achievement_key)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
        """, (user_id, achievement_key))

        conn.commit()

    except Exception as e:
        print("ADD ACHIEVEMENT ERROR:", e)
        conn.rollback()

    finally:
        cur.close()
        release_conn(conn)

def has_achievement(user_id, achievement_key):
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
        SELECT 1 FROM achievements
        WHERE user_id = %s AND achievement_key = %s
        """, (user_id, achievement_key))

        return cur.fetchone() is not None

    except Exception as e:
        print("CHECK ACHIEVEMENT ERROR:", e)
        return False

    finally:
        cur.close()
        release_conn(conn)

def get_user_achievements(user_id):
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
        SELECT achievement_key FROM achievements
        WHERE user_id = %s
        """, (user_id,))

        return [row[0] for row in cur.fetchall()]

    except Exception as e:
        print("GET USER ACHIEVEMENTS ERROR:", e)
        return []

    finally:
        cur.close()
        release_conn(conn)
