import bcrypt
import sqlite3

def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def register_user(username: str, password: str):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (username TEXT PRIMARY KEY, password TEXT)''')
    
    hashed_password = hash_password(password)
    
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?,?)", 
                       (username, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        print("El usuario ya existe.")
    finally:
        conn.close()

def verify_password(username: str, password: str) -> bool:
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT password FROM users WHERE username =?", (username,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return bcrypt.checkpw(password.encode('utf-8'), result[0])
    return False
