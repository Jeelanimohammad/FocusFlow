
import sqlite3
from datetime import datetime

# ================= CONNECTION =================
def get_connection():
    return sqlite3.connect("focusflow.db", check_same_thread=False)


# ================= CREATE TABLES =================
def create_tables():
    conn = get_connection()
    c = conn.cursor()

    # USERS (FIXED: password as BLOB)
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password BLOB
    )
    """)

    # TASKS
    c.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        subject TEXT,
        deadline TEXT,
        hours_per_day INTEGER,
        difficulty TEXT DEFAULT 'Medium',
        status TEXT DEFAULT 'Pending'
    )
    """)

    # STUDY LOG
    c.execute("""
    CREATE TABLE IF NOT EXISTS study_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        minutes INTEGER
    )
    """)

    conn.commit()
    conn.close()


# ================= TASK FUNCTIONS =================
def add_task(user_id, subject, deadline, hours, difficulty):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    INSERT INTO tasks (user_id, subject, deadline, hours_per_day, difficulty, status)
    VALUES (?, ?, ?, ?, ?, 'Pending')
    """, (user_id, subject, deadline, hours, difficulty))

    conn.commit()
    conn.close()


def get_tasks(user_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM tasks WHERE user_id=?", (user_id,))
    data = c.fetchall()

    conn.close()
    return data


def delete_task(task_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()


def update_task_status(task_id, status):
    conn = get_connection()
    c = conn.cursor()

    c.execute("UPDATE tasks SET status=? WHERE id=?", (status, task_id))

    conn.commit()
    conn.close()


# ================= STUDY TIME =================
def log_study_time(user_id, minutes):
    conn = get_connection()
    c = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    c.execute("SELECT * FROM study_log WHERE user_id=? AND date=?", (user_id, today))
    row = c.fetchone()

    if row:
        c.execute("""
        UPDATE study_log SET minutes = minutes + ?
        WHERE user_id=? AND date=?
        """, (minutes, user_id, today))
    else:
        c.execute("""
        INSERT INTO study_log (user_id, date, minutes)
        VALUES (?, ?, ?)
        """, (user_id, today, minutes))

    conn.commit()
    conn.close()
