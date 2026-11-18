import bcrypt
import sqlite3

def hash_password(password: str) -> bytes:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password

def register_user(username: str, password: str):
    hashed_password = hash_password(password)
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (username TEXT PRIMARY KEY, password TEXT)''')
    
    cursor.execute("INSERT INTO users (username, password) VALUES (?,?)",
                   (username, hashed_password))
    
    conn.commit()
    conn.close()

def verify_password(username: str, password: str) -> bool:
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT password FROM users WHERE username =?", (username,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        stored_hashed_password = result[0]
        password_bytes = password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, stored_hashed_password)
    
    return False
