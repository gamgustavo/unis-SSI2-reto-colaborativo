import bcrypt
import sqlite3

def hash_password(password: str) -> bytes:
    """Hash a password for storing."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def verify_password(stored_password: bytes, provided_password: str) -> bool:
    """Verify a stored password against one provided by the user."""
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)

def register_user(username: str, password: str):
    """Register a new user with a hashed password."""
    hashed_password = hash_password(password)
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (username TEXT PRIMARY KEY, password TEXT)''')
    
    cursor.execute("INSERT INTO users (username, password) VALUES (?,?)",
                   (username, hashed_password))
    conn.commit()
    conn.close()

def verify_user(username: str, password: str) -> bool:
    """Verify user's password."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT password FROM users WHERE username =?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if row is not None:
        return verify_password(row[0], password)
    return False
