import hashlib
import logging
from getpass import getpass

logging.basicConfig(filename='login_attempts.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def hash_password(password):
    salt = "random_salt_here"  # Ideally, use a random salt for each user
    hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()
    return hashed_password

def login(username, password):
    valid_users = {
        "user1": hash_password("password1"),
        "user2": hash_password("password2")
    }
    
    attempt_password = hash_password(password)
    
    if username in valid_users and valid_users[username] == attempt_password:
        logging.info(f"Successful login attempt for user: {username}")
        return True
    else:
        logging.warning(f"Failed login attempt for user: {username} with password: {password}")
        return False

def main():
    username = input("Enter your username: ")
    password = getpass("Enter your password: ")
    
    if login(username, password):
        print("Login successful!")
    else:
        print("Login failed. Please check your username and password.")

if __name__ == "__main__":
    main()
