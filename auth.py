import sqlite3
import hashlib

def get_connection():
    return sqlite3.connect("focusflow.db", check_same_thread=False)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_password(password):
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    if not any(char.isdigit() for char in password):
        return False, "Password must contain a number"
    if not any(char.isupper() for char in password):
        return False, "Password must contain an uppercase letter"
    return True, ""

def register_user(username, password):
    valid, message = validate_password(password)
    if not valid:
        return False, message

    conn = get_connection()
    c = conn.cursor()

    hashed_pw = hash_password(password)

    try:
        c.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_pw)
        )
        conn.commit()
        conn.close()
        return True, "Account created successfully"
    except:
        conn.close()
        return False, "Username already exists"

def login_user(username, password):
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()

    if user:
        stored_password = user[2]
        if hash_password(password) == stored_password:
            return user

    return None
