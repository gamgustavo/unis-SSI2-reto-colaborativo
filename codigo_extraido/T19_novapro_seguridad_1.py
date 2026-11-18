import hashlib
import logging
from getpass import getpass

logging.basicConfig(filename='login_attempts.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def hash_password(password):
    salt = 'unique_salt'  # Consider using a more secure method to generate and store salts
    hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()
    return hashed_password

def login():
    username = input("Enter username: ")
    password = getpass("Enter password: ")
    
    logging.info(f"Login attempt for user: {username}")
    
    # Simulate a stored hashed password for the user (in a real application, fetch this from a database)
    stored_hashed_password = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"  # hashed value for "password"
    
    if hash_password(password) == stored_hashed_password:
        print("Login successful")
    else:
        print("Login failed")

if __name__ == "__main__":
    login()
