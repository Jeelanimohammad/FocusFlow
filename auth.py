
import sqlite3
import bcrypt

# ================= DB CONNECTION =================
def get_connection():
    return sqlite3.connect("focusflow.db", check_same_thread=False)


# ================= PASSWORD VALIDATION =================
def validate_password(password):
    if len(password) < 6:
        return False, "Password must be at least 6 characters"

    if not any(char.isdigit() for char in password):
        return False, "Password must contain a number"

    if not any(char.isupper() for char in password):
        return False, "Password must contain an uppercase letter"

    return True, ""


# ================= REGISTER =================
def register_user(username, password):
    valid, message = validate_password(password)

    if not valid:
        return False, message

    conn = get_connection()
    c = conn.cursor()

    # HASH PASSWORD (bytes)
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

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


# ================= LOGIN =================
def login_user(username, password):
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()

    conn.close()

    if user:
        stored_password = user[2]

        # Ensure password is bytes
        if isinstance(stored_password, str):
            stored_password = stored_password.encode('utf-8')

        if bcrypt.checkpw(password.encode('utf-8'), stored_password):
            return user

    return None
