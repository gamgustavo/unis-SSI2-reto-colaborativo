import bcrypt
import sqlite3

def create_connection():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                     (username TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    return conn

def register_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?,?)", 
                       (username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_password(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT password FROM users WHERE username =?", (username,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result and bcrypt.checkpw(password.encode('utf-8'), result[0]):
        return True
    return False
