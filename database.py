import os
import sqlite3
from datetime import datetime, timezone, timedelta

DB_NAME = os.getenv("DB_PATH", "mindex.db")

ALGERIA = timezone(timedelta(hours=1))


def connect():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def now():
    return datetime.now(ALGERIA)


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
                correct INTEGER DEFAULT 0,
                created_at TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS score_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                points INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                attempt_type TEXT NOT NULL,
                attempt_date TEXT NOT NULL,
                status TEXT DEFAULT 'in_progress',
                score INTEGER DEFAULT 0,
                correct INTEGER DEFAULT 0,
                total INTEGER DEFAULT 0,
                question_data TEXT DEFAULT '',
                current_index INTEGER DEFAULT 0,
                UNIQUE(user_id, attempt_type, attempt_date)
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_date
            ON score_events(created_at)
        """)


def register_student(user_id, full_name):
    with connect() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO students
            (user_id, full_name, created_at)
            VALUES (?, ?, ?)
        """, (user_id, full_name, now().isoformat()))


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


def add_xp(user_id, points, event_type="general"):
    with connect() as conn:
        conn.execute("""
            UPDATE students
            SET xp = xp + ?
            WHERE user_id = ?
        """, (points, user_id))

        conn.execute("""
            INSERT INTO score_events
            (user_id, points, event_type, created_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, points, event_type, now().isoformat()))


def save_quiz_result(user_id, points, correct):
    with connect() as conn:
        conn.execute("""
            UPDATE students
            SET xp = xp + ?,
                quizzes = quizzes + 1,
                correct = correct + ?
            WHERE user_id = ?
        """, (points, correct, user_id))

        conn.execute("""
            INSERT INTO score_events
            (user_id, points, event_type, created_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, points, "quiz", now().isoformat()))


def get_ranking(limit=10, period="all"):
    start = period_start(period)

    with connect() as conn:
        if start is None:
            return conn.execute("""
                SELECT full_name, wilaya, branch, xp
                FROM students
                ORDER BY xp DESC
                LIMIT ?
            """, (limit,)).fetchall()

        return conn.execute("""
            SELECT s.full_name, s.wilaya, s.branch,
                   COALESCE(SUM(e.points), 0) AS xp
            FROM students s
            LEFT JOIN score_events e
              ON s.user_id = e.user_id
              AND e.created_at >= ?
            GROUP BY s.user_id
            ORDER BY xp DESC
            LIMIT ?
        """, (start, limit)).fetchall()


def period_start(period):
    current = now()

    if period == "daily":
        return current.replace(
            hour=0, minute=0, second=0, microsecond=0
        ).isoformat()

    if period == "weekly":
        start = current - timedelta(days=current.weekday())
        return start.replace(
            hour=0, minute=0, second=0, microsecond=0
        ).isoformat()

    if period == "monthly":
        return current.replace(
            day=1, hour=0, minute=0,
            second=0, microsecond=0
        ).isoformat()

    return None


def get_group_ranking(group, period="monthly"):
    column = "wilaya" if group == "wilaya" else "branch"
    start = period_start(period)

    with connect() as conn:
        return conn.execute(f"""
            SELECT s.{column} AS name,
                   COALESCE(SUM(e.points), 0) AS points
            FROM students s
            LEFT JOIN score_events e
              ON s.user_id = e.user_id
              AND e.created_at >= ?
            WHERE s.{column} != ''
            GROUP BY s.{column}
            ORDER BY points DESC
        """, (start,)).fetchall()


def get_attempt(user_id, attempt_type):
    today = now().date().isoformat()

    with connect() as conn:
        return conn.execute("""
            SELECT * FROM attempts
            WHERE user_id = ?
              AND attempt_type = ?
              AND attempt_date = ?
        """, (user_id, attempt_type, today)).fetchone()


def create_attempt(user_id, attempt_type, total, question_data):
    today = now().date().isoformat()

    with connect() as conn:
        cursor = conn.execute("""
            INSERT OR IGNORE INTO attempts
            (user_id, attempt_type, attempt_date,
             total, question_data)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id, attempt_type, today,
            total, question_data
        ))

        return cursor.rowcount == 1


def update_attempt(user_id, attempt_type, score,
                   correct, current_index):
    today = now().date().isoformat()

    with connect() as conn:
        conn.execute("""
            UPDATE attempts
            SET score = ?,
                correct = ?,
                current_index = ?
            WHERE user_id = ?
              AND attempt_type = ?
              AND attempt_date = ?
        """, (
            score, correct, current_index,
            user_id, attempt_type, today
        ))


def finish_attempt(user_id, attempt_type):
    today = now().date().isoformat()

    with connect() as conn:
        conn.execute("""
            UPDATE attempts
            SET status = 'completed'
            WHERE user_id = ?
              AND attempt_type = ?
              AND attempt_date = ?
        """, (user_id, attempt_type, today))
