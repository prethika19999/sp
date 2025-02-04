import json
import hashlib
import os

USER_DATA_FILE = "user_data.json"

def hash_password(password):
    """Hash the password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def load_user_data():
    """Load user data from a JSON file."""
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    return {}

def save_user_data(user_data):
    """Save user data to a JSON file."""
    with open(USER_DATA_FILE, "w") as file:
        json.dump(user_data, file)

def sign_up(username, password, age, sex, location, favorite_genre):
    """Sign up a new user."""
    user_data = load_user_data()
    if username in user_data:
        return False  # Username already exists
    user_data[username] = {
        "password": hash_password(password),
        "age": age,
        "sex": sex,
        "location": location,
        "favorite_genre": favorite_genre
    }
    save_user_data(user_data)
    return True

def login(username, password):
    """Login user by verifying credentials."""
    user_data = load_user_data()
    hashed_password = hash_password(password)
    if username in user_data and user_data[username]["password"] == hashed_password:
        return True
    return False
