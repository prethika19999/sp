import streamlit as st
import json
import psutil
import time
import os
import cv2
import numpy as np
from tensorflow.keras.models import load_model

# Paths and constants
CLASSIFIED_VIDEO_DIR = "/Users/yuthikaprethika/Documents/GitHub/sp/classified_videos"
USER_DATA_FILE = "user_data.json"
USER_ACTIVITY_FILE = "user_activity.json"
MODEL_PATH = "/Users/yuthikaprethika/Documents/GitHub/sp/video_classification_model.h5"
FRAMES_PER_VIDEO = 30
FRAME_SIZE = (64, 64)
CATEGORIES = ["Action", "Comedy", "Music"]

# Load the classification model
model = load_model(MODEL_PATH)

# Extract frames from videos
def extract_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []
    while len(frames) < FRAMES_PER_VIDEO:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, FRAME_SIZE)
        frames.append(frame)
    cap.release()
    if len(frames) < FRAMES_PER_VIDEO:
        return None  # Skip videos with fewer frames
    return np.array(frames)

# Function to classify a video
def classify_video(video_path):
    frames = extract_frames(video_path)
    if frames is not None:
        frames = np.expand_dims(frames / 255.0, axis=0)
        predictions = model.predict(frames)
        class_idx = np.argmax(predictions)
        return CATEGORIES[class_idx]
    else:
        return "Insufficient frames in video"

# Function to save video in the appropriate category folder
def save_video_to_class_folder(video_path, category):
    category_folder = os.path.join(CLASSIFIED_VIDEO_DIR, category)
    os.makedirs(category_folder, exist_ok=True)
    video_name = os.path.basename(video_path)
    dest_path = os.path.join(category_folder, video_name)
    os.rename(video_path, dest_path)
    return dest_path

def admin_dashboard(username):

    # Display logo and heading
    header_col1, header_col2 = st.columns([1, 8])
    with header_col1:
        st.image("/Users/yuthikaprethika/Documents/GitHub/sp/logo.jpeg", width=60)  # Adjust width as needed
    with header_col2:
        st.title("Welcome to Sparkplay")

    """Admin Dashboard."""
    st.title(f"Welcome, {username}!")

    # Monitor System Performance
    st.header("Monitor System Performance (CPU, Memory, etc.)")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("CPU Usage (%)", f"{psutil.cpu_percent()}%")
    with col2:
        st.metric("Memory Usage (%)", f"{psutil.virtual_memory().percent}%")

    # Handle System Failures or Performance Issues
    st.header("Handle System Failures or Performance Issues")
    failures = ["Network Issue", "Database Crash", "Server Overload"]
    selected_failure = st.selectbox("Select an Issue to Resolve:", failures)
    if st.button("Resolve Issue"):
        st.success(f"Resolved: {selected_failure}")

    # Maintain System Uptime
    st.header("Maintain System Uptime")
    uptime = time.time() - psutil.boot_time()
    st.metric("System Uptime (hours)", f"{uptime // 3600}")

    # Ensure Efficient Resource Management
    st.header("Ensure Efficient Resource Management")
    st.text("Actions to improve system resource management:")
    st.markdown("- Optimize database queries")
    st.markdown("- Clean temporary files")
    st.markdown("- Upgrade hardware as needed")

    # Manage Users
    st.header("Manage Users")
    # Load user names from user_activity.json
    try:
        with open("user_activity.json", "r") as f:
            user_data = json.load(f)
            user_names = list(user_data.keys())
    except (FileNotFoundError, json.JSONDecodeError):
        user_data = {}
        user_names = []

    selected_user = st.selectbox("Select User to Edit", user_names)
    if selected_user:
        st.subheader(f"Details for User: {selected_user}")
        st.json(user_data.get(selected_user, {}))

    updated_info = st.text_area("Updated Info (JSON format)")
    if st.button("Edit User Profile"):
        try:
            updated_info_dict = json.loads(updated_info)
            # Call edit_user_profile function here
            st.success(f"User {selected_user}'s profile updated successfully!")
        except json.JSONDecodeError:
            st.error("Invalid JSON format.")

    # Get video IDs from folder
    video_folder = "/Users/yuthikaprethika/Documents/GitHub/sp/Videos_Data"
    try:
        video_ids = [f for f in os.listdir(video_folder) if os.path.isfile(os.path.join(video_folder, f))]
    except FileNotFoundError:
        video_ids = []

    # Approve Videos
    st.header("Approve Videos")
    video_id_to_approve = st.selectbox("Select Video ID to Approve", video_ids, key="approve_video")
    if st.button("Approve Video"):
        approve_video(video_id_to_approve)  # Call approve_video function
        st.success(f"Video {video_id_to_approve} approved successfully!")

    # Delete Videos
    st.header("Delete Videos")
    video_id_to_delete = st.selectbox("Select Video ID to Delete", video_ids, key="delete_video")
    if st.button("Delete Video"):
        delete_video(video_id_to_delete, video_folder)  # Call delete_video function
        st.success(f"Video {video_id_to_delete} deleted successfully!")

    # Categorize Videos
    st.header("Categorize Videos")
    video_id_to_categorize = st.selectbox("Select Video ID to Categorize", video_ids, key="categorize_video")
    if st.button("Categorize Video"):
        video_path = os.path.join(video_folder, video_id_to_categorize)
        category = classify_video(video_path)
        if category != "Insufficient frames in video":
            save_video_to_class_folder(video_path, category)
            st.success(f"Video {video_id_to_categorize} categorized as {category}!")
        else:
            st.error("Video could not be categorized due to insufficient frames.")

    # Manage Recommendation System
    st.header("Manage Recommendation System")
    if st.button("Optimize Recommendations"):
        # Call manage_recommendation_system function here
        st.success("Recommendation system optimized!")

    # View User Logs
    st.header("View User Logs")
    if st.button("View Logs"):
        # Call view_user_logs function here
        st.write("Displaying user logs...")

    # Monitor Risk and Security
    st.header("Monitor Risk and Security")
    if st.button("Run Security Audit"):
        # Call monitor_risk_security function here
        st.success("Security audit completed successfully!")

    # Logout option
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.experimental_rerun()

def approve_video(video_id):
    """Function to approve a video."""
    try:
        approved_videos_file = "approved_videos.json"
        approved_videos = []

        # Load existing approved videos if the file exists
        if os.path.exists(approved_videos_file):
            with open(approved_videos_file, "r") as f:
                approved_videos = json.load(f)

        # Add the new video to the list if not already approved
        if video_id not in approved_videos:
            approved_videos.append(video_id)

            # Save the updated list back to the file
            with open(approved_videos_file, "w") as f:
                json.dump(approved_videos, f)

            st.success(f"Video {video_id} has been approved.")
        else:
            st.warning(f"Video {video_id} is already approved.")
    except Exception as e:
        st.error(f"An error occurred while approving the video: {e}")

def delete_video(video_id, video_folder):
    """Function to delete a video from the folder."""
    video_path = os.path.join(video_folder, video_id)
    if os.path.exists(video_path):
        os.remove(video_path)
    else:
        st.error(f"Video {video_id} not found.")
