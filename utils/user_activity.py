import json
import os
from datetime import datetime

USER_ACTIVITY_FILE = "user_activity.json"
CHAT_MESSAGES_FILE = "chat_messages.json"

def load_user_activity():
    """Load user activity data from a JSON file."""
    if os.path.exists(USER_ACTIVITY_FILE):
        with open(USER_ACTIVITY_FILE, "r") as file:
            return json.load(file)
    return {}

def save_user_activity(activity_data):
    """Save user activity data to a JSON file."""
    with open(USER_ACTIVITY_FILE, "w") as file:
        json.dump(activity_data, file, indent=4)

def load_chat_messages():
    """Load chat messages data from a JSON file."""
    if os.path.exists(CHAT_MESSAGES_FILE):
        with open(CHAT_MESSAGES_FILE, "r") as file:
            return json.load(file)
    return {}

def save_chat_messages(chat_data):
    """Save chat messages data to a JSON file."""
    with open(CHAT_MESSAGES_FILE, "w") as file:
        json.dump(chat_data, file, indent=4)

def get_user_activity(username):
    """Retrieve activity data for a specific user."""
    activity_data = load_user_activity()
    return activity_data.get(username, {"liked": [], "disliked": [], "comments": {}, "shares": []})

def update_like(username, video_id):
    """Update the like status for a specific video by a user."""
    activity_data = load_user_activity()
    user_activity = activity_data.setdefault(username, {"liked": [], "disliked": [], "comments": {}, "shares": []})

    if video_id in user_activity["liked"]:
        user_activity["liked"].remove(video_id)
    else:
        user_activity["liked"].append(video_id)
        if video_id in user_activity["disliked"]:
            user_activity["disliked"].remove(video_id)
    
    save_user_activity(activity_data)

def update_dislike(username, video_id):
    """Update the dislike status for a specific video by a user."""
    activity_data = load_user_activity()
    user_activity = activity_data.setdefault(username, {"liked": [], "disliked": [], "comments": {}, "shares": []})

    if video_id in user_activity["disliked"]:
        user_activity["disliked"].remove(video_id)
    else:
        user_activity["disliked"].append(video_id)
        if video_id in user_activity["liked"]:
            user_activity["liked"].remove(video_id)
    
    save_user_activity(activity_data)

def add_comment(username, video_id, comment_text):
    """Add a comment by a user to a specific video."""
    activity_data = load_user_activity()
    user_activity = activity_data.setdefault(username, {"liked": [], "disliked": [], "comments": {}, "shares": []})

    if video_id not in user_activity["comments"]:
        user_activity["comments"][video_id] = []
    
    user_activity["comments"][video_id].append({
        "comment": comment_text,
        "timestamp": datetime.now().isoformat()
    })
    
    save_user_activity(activity_data)

def share_video(username, video_id):
    """Track when a user shares a video."""
    activity_data = load_user_activity()
    user_activity = activity_data.setdefault(username, {"liked": [], "disliked": [], "comments": {}, "shares": []})

    if video_id not in user_activity["shares"]:
        user_activity["shares"].append(video_id)
    
    save_user_activity(activity_data)

def get_user_likes(username):
    """Retrieve the list of videos liked by the user."""
    activity_data = load_user_activity()
    user_activity = activity_data.get(username, {"liked": [], "disliked": [], "comments": {}, "shares": []})
    return user_activity["liked"]

def get_user_history(username):
    """Retrieve the list of videos viewed by the user."""
    activity_data = load_user_activity()
    user_activity = activity_data.get(username, {"liked": [], "disliked": [], "comments": {}, "shares": []})
    return user_activity.get("viewed", [])  # Ensure "viewed" is tracked

def track_view(username, video_id):
    """Track when a user views a video."""
    activity_data = load_user_activity()
    user_activity = activity_data.setdefault(username, {"liked": [], "disliked": [], "comments": {}, "shares": [], "viewed": []})
    
    if video_id not in user_activity["viewed"]:
        user_activity["viewed"].append(video_id)
    
    save_user_activity(activity_data)

def fetch_chat_messages(video_id):
    """Fetch all chat messages for a specific video."""
    chat_data = load_chat_messages()
    return chat_data.get(video_id, [])

def send_chat_message(username, video_id, message_text):
    """Send a chat message for a specific video."""
    chat_data = load_chat_messages()
    video_chat = chat_data.setdefault(video_id, [])

    video_chat.append({
        "username": username,
        "message": message_text,
        "timestamp": datetime.now().isoformat()
    })
    
    save_chat_messages(chat_data)

def fetch_user_chat(sender, recipient):
    """Fetch chat messages between two users."""
    chat_data = load_chat_messages()
    return chat_data.get(f"{sender}_{recipient}", []) + chat_data.get(f"{recipient}_{sender}", [])

def send_user_message(sender, recipient, message_text):
    """Send a chat message between users."""
    chat_data = load_chat_messages()
    conversation_key = f"{sender}_{recipient}"
    if conversation_key not in chat_data:
        chat_data[conversation_key] = []
    chat_data[conversation_key].append({
        "sender": sender,
        "message": message_text,
        "timestamp": datetime.now().isoformat()
    })
    save_chat_messages(chat_data)

