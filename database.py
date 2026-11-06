
import sqlite3

DB_NAME = "mindex.db"


def connect():
    return sqlite3.connect(DB_NAME)


def init_db():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT,
                branch TEXT DEFAULT '',
                wilaya TEXT DEFAULT '',
                xp INTEGER DEFAULT 0,
                quizzes INTEGER DEFAULT 0,
                correct INTEGER DEFAULT 0
            )
        """)


def register_student(user_id, full_name):
    with connect() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO students
            (user_id, full_name)
            VALUES (?, ?)
        """, (user_id, full_name))


def get_student(user_id):
    with connect() as conn:
        return conn.execute("""
            SELECT * FROM students
            WHERE user_id = ?
        """, (user_id,)).fetchone()


def update_branch(user_id, branch):
    with connect() as conn:
        conn.execute("""
            UPDATE students
            SET branch = ?
            WHERE user_id = ?
        """, (branch, user_id))


def update_wilaya(user_id, wilaya):
    with connect() as conn:
        conn.execute("""
            UPDATE students
            SET wilaya = ?
            WHERE user_id = ?
        """, (wilaya, user_id))


def add_xp(user_id, points):
    with connect() as conn:
        conn.execute("""
            UPDATE students
            SET xp = xp + ?
            WHERE user_id = ?
        """, (points, user_id))


def save_quiz_result(user_id, points, correct):
    with connect() as conn:
        conn.execute("""
            UPDATE students
            SET xp = xp + ?,
                quizzes = quizzes + 1,
                correct = correct + ?
            WHERE user_id = ?
        """, (points, correct, user_id))


def get_ranking(limit=10):
    with connect() as conn:
        return conn.execute("""
            SELECT full_name, xp
            FROM students
            ORDER BY xp DESC
            LIMIT ?
        """, (limit,)).fetchall()


def get_wilaya_ranking(wilaya, limit=10):
    with connect() as conn:
        return conn.execute("""
            SELECT full_name, xp
            FROM students
            WHERE wilaya = ?
            ORDER BY xp DESC
            LIMIT ?
        """, (wilaya, limit)).fetchall()
