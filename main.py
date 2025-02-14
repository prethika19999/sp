import streamlit as st
import os
import json
import numpy as np
import smtplib
import random
from email.mime.text import MIMEText
from sklearn.metrics.pairwise import cosine_similarity
from utils.user_auth import login, sign_up
from utils.user_activity import (update_like, update_dislike, add_comment, share_video, track_view)
from utils.user_activity import (get_user_activity, update_like, update_dislike, add_comment, share_video, fetch_chat_messages, send_chat_message, track_view, send_user_message, fetch_user_chat)
from utils.data import video_metadata  # Import video metadata from a separate file
from users.developer import developer_dashboard
from users.data_analyst import data_analyst_dashboard
from users.product_manager import product_manager_dashboard
from users.advertiser import advertiser_dashboard
from users.system_administrator import system_administrator_dashboard
from users.admin import admin_dashboard
from tensorflow.keras.models import load_model
import cv2
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import StringType, StructType, StructField

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("Video Recommendation App") \
    .config("spark.driver.memory", "2g") \
    .getOrCreate()

# Set up Streamlit page
st.set_page_config(page_title="Sparkplay", layout="wide")

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
if "show_login" not in st.session_state:
    st.session_state.show_login = False
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False
if "current_video" not in st.session_state:
    st.session_state.current_video = None
if "user_interactions" not in st.session_state:
    st.session_state.user_interactions = []
if "history" not in st.session_state:
    st.session_state.history = []
if "liked_videos" not in st.session_state:
    st.session_state.liked_videos = []
if "otp" not in st.session_state:
    st.session_state.otp = None
if "otp_verified" not in st.session_state:
    st.session_state.otp_verified = False
if "offline_mode" not in st.session_state:
    st.session_state.offline_mode = False

# Constants and Paths
VIDEO_UPLOAD_DIR = "uploaded_videos"
CLASSIFIED_VIDEO_DIR = "classified_videos"
USER_DATA_FILE = "user_data.json"
USER_ACTIVITY_FILE = "user_activity.json"
MODEL_PATH = "video_classification_model.h5"
FRAMES_PER_VIDEO = 30
FRAME_SIZE = (64, 64)
CATEGORIES = ["Action", "Comedy", "Music"]

# Load the video classification model
model = load_model("video_classification_model.h5")

# Function to cache video metadata
def cache_video_metadata(video_metadata, cache_file="video_metadata_cache.json"):
    with open(cache_file, "w") as file:
        json.dump(video_metadata, file)

# Function to cache user interactions
def cache_user_interactions(user_interactions, cache_file="user_interactions_cache.json"):
    with open(cache_file, "w") as file:
        json.dump(user_interactions, file)

# Function to load cached video metadata
def load_cached_video_metadata(cache_file="video_metadata_cache.json"):
    if os.path.exists(cache_file):
        with open(cache_file, "r") as file:
            return json.load(file)
    return []

# Function to load cached user interactions
def load_cached_user_interactions(cache_file="user_interactions_cache.json"):
    if os.path.exists(cache_file):
        with open(cache_file, "r") as file:
            return json.load(file)
    return []

# Function to extract frames from video
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
        return None
    return np.array(frames)

# Function to classify video
def classify_video(video_path):
    frames = extract_frames(video_path)
    if frames is not None:
        frames = np.expand_dims(frames / 255.0, axis=0)
        predictions = model.predict(frames)
        class_idx = np.argmax(predictions)
        return CATEGORIES[class_idx]
    else:
        return "Insufficient frames"

# Function to save video to category folder
def save_video_to_class_folder(video_path, category):
    category_folder = os.path.join(CLASSIFIED_VIDEO_DIR, category)
    os.makedirs(category_folder, exist_ok=True)
    video_name = os.path.basename(video_path)
    dest_path = os.path.join(category_folder, video_name)
    os.rename(video_path, dest_path)
    return dest_path

# Function to send generic email
def send_email(sender_email, sender_password, receiver_email, subject, body):
    try:
        msg = MIMEText(body)
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()

        st.success('Email sent successfully! 🚀')
    except Exception as e:
        st.error(f"Error while sending email: {e}")

# Function to send OTP to email
def send_otp(email):
    otp = random.randint(100000, 999999)
    st.session_state.otp = otp
    sender_email = "sparkplay4@gmail.com"
    sender_password = "fjloeusfxyepjemq"

    # Create email message
    subject = "Sign Up OTP Verification"
    body = f"Your OTP for Sign Up is: {otp}"

    send_email(sender_email, sender_password, email, subject, body)

# Function to fetch user_ids dynamically
def fetch_user_ids():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as file:
            user_data = json.load(file)
        return list(user_data.keys())
    return []

# Function to load user activity as a PySpark DataFrame
def load_user_activity():
    schema = StructType([
        StructField("User_ID", StringType(), True),
        StructField("Video_ID", StringType(), True),
        StructField("Interaction_Type", StringType(), True)
    ])

    if os.path.exists(USER_ACTIVITY_FILE):
        return spark.read.json(USER_ACTIVITY_FILE, schema=schema)
    else:
        return spark.createDataFrame([], schema=schema)

# Function to create an interaction matrix
def create_interaction_matrix(user_interactions, video_metadata, user_ids):
    video_ids = [video["Video_ID"] for video in video_metadata]
    interaction_matrix = np.zeros((len(user_ids), len(video_ids)))
    for interaction in user_interactions:
        user_idx = user_ids.index(interaction["User_ID"])
        video_idx = video_ids.index(interaction["Video_ID"])
        if interaction["Interaction_Type"] == "like":
            interaction_matrix[user_idx, video_idx] = 1
        elif interaction["Interaction_Type"] == "view":
            interaction_matrix[user_idx, video_idx] = 0.5
    return interaction_matrix

# Function to recommend videos
def recommend_videos_cf(user_id, interaction_matrix=None, video_metadata=None, user_ids=None, num_recommendations=3):
    # Load cached data if no data is provided
    if interaction_matrix is None or video_metadata is None or user_ids is None:
        video_metadata = load_cached_video_metadata()
        user_interactions = load_cached_user_interactions()
        user_ids = fetch_user_ids()
        interaction_matrix = create_interaction_matrix(user_interactions, video_metadata, user_ids)

    # Proceed with the recommendation logic
    video_ids = [video["Video_ID"] for video in video_metadata]
    user_idx = user_ids.index(user_id)
    user_ratings = interaction_matrix[user_idx]

    # Calculate video similarity
    video_similarity = cosine_similarity(interaction_matrix.T)

    # Compute recommendation scores
    recommendations = video_similarity.dot(user_ratings)
    recommendations[user_ratings > 0] = -1  # Exclude watched/liked videos

    # Get top recommendations
    recommended_video_indices = np.argsort(recommendations)[::-1][:num_recommendations]
    return [video_metadata[i] for i in recommended_video_indices]

# Function to log user activity
def log_user_activity(user_id, video_id, interaction_type):
    user_activity_df = load_user_activity()

    # Create a new row for the interaction
    new_interaction = [(user_id, video_id, interaction_type)]
    new_interaction_df = spark.createDataFrame(new_interaction, ["User_ID", "Video_ID", "Interaction_Type"])

    # Append the new interaction
    updated_user_activity_df = user_activity_df.union(new_interaction_df)

    # Save updated activity back to JSON
    updated_user_activity_df.write.json(USER_ACTIVITY_FILE, mode="overwrite")

# Cache video metadata and user interactions when the app starts
if st.session_state.logged_in:
    cache_video_metadata(video_metadata)
    cache_user_interactions(st.session_state.user_interactions)

# Add a toggle for offline mode
offline_mode = st.sidebar.checkbox("Offline Mode", key="offline_mode")

if offline_mode:
    st.sidebar.info("You are in offline mode. Recommendations are based on cached data.")
else:
    st.sidebar.info("You are in online mode. Recommendations are based on live data.")

# Top-right buttons for Sign In, Sign Up, and Logout
col1, col2, col3, col4 = st.columns([7, 1, 1, 1])
if not st.session_state.logged_in:
    with col2:
        if st.button("Sign In", key="signin_top"):
            st.session_state.show_login = True
            st.session_state.show_signup = False
    with col3:
        if st.button("Sign Up", key="signup_top"):
            st.session_state.show_signup = True
            st.session_state.show_login = False
else:
    with col3:
        if st.button("Logout", key="logout_top"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.experimental_set_query_params(rerun="true")  # Trigger rerun to refresh the app

    with col4:
        st.markdown("<style>.stFileUploader {padding: 0;}</style>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("", type=["mp4", "avi", "mov"], label_visibility="collapsed", key="upload_video_button")
        upload_button = st.button("Upload Video", key="upload_video_action")

        if uploaded_file is not None and upload_button:
            # Save the uploaded video to the upload directory
            video_path = os.path.join(VIDEO_UPLOAD_DIR, uploaded_file.name)
            with open(video_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("Video uploaded successfully!")

            # Classify the video
            category = classify_video(video_path)
            if category != "Insufficient frames":
                # Save the video in the appropriate class folder
                classified_path = save_video_to_class_folder(video_path, category)
                st.success(f"Video classified as '{category}' and saved to {classified_path}")
            else:
                st.error("Video classification failed due to insufficient frames.")

            # Add the uploaded video to the session state for real-time updates
            if "new_uploaded_videos" not in st.session_state:
                st.session_state.new_uploaded_videos = []
            st.session_state.new_uploaded_videos.append({
                "Path": classified_path,
                "Title": uploaded_file.name,
                "Category": category,
            })

# Display Login or Sign Up Forms
if st.session_state.show_login:
    # Display logo and heading
    header_col1, header_col2 = st.columns([1, 8])
    with header_col1:
        st.image("logo.jpeg", width=60)  # Adjust width as needed
    with header_col2:
        st.title("Welcome to Sparkplay")

    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_button"):
        if login(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.show_login = False
            st.success("Login successful!")
            st.experimental_set_query_params(rerun="true")  # Trigger rerun after login
        else:
            st.error("Invalid username or password.")

elif st.session_state.show_signup:
    # Display logo and heading
    header_col1, header_col2 = st.columns([1, 8])
    with header_col1:
        st.image("logo.jpeg", width=60)  # Adjust width as needed
    with header_col2:
        st.title("Welcome to Sparkplay")

    st.subheader("Sign Up")
    username = st.text_input("Username", key="signup_username")
    password = st.text_input("Password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
    email = st.text_input("Email")
    age = st.text_input("Age")
    location = st.selectbox("Location", ["India", "London", "USA", "Singapore"], key="signup_location")
    favorite_genre = st.selectbox("Favorite Genre", ["Action", "Comedy", "Music"], key="signup_genre")

    if st.button("Send OTP", key="send_otp_button"):
        if email:
            send_otp(email)
        else:
            st.error("Please enter a valid email.")

    otp = st.text_input("Enter OTP", key="otp_input")

    if st.button("Verify OTP", key="verify_otp_button"):
        if otp and int(otp) == st.session_state.otp:
            st.success("OTP verified successfully!")
            st.session_state.otp_verified = True
        else:
            st.error("Invalid OTP. Please try again.")

    if st.button("Sign Up", key="signup_button"):
        if password != confirm_password:
            st.error("Passwords do not match.")
        elif not username or not password or not email or not favorite_genre:
            st.error("Please fill out all fields.")
        elif not st.session_state.otp_verified:
            st.error("Please verify your OTP before signing up.")
        elif sign_up(username, password, email, age, location, favorite_genre):
            st.success("Sign up successful! You can now log in.")
            st.session_state.show_signup = False
        else:
            st.error("Username already exists. Please choose a different username.")

# Default dashboard for non-logged-in users
if not st.session_state.logged_in:
    # Banner for non-logged-in users
    st.markdown(
        """
        <div style='
            background-color: #f9f9f9; 
            border: 2px solid #ddd; 
            border-radius: 10px; 
            padding: 20px; 
            text-align: center;
            margin-bottom: 20px;
            font-family: Arial, sans-serif;
        '>
            <h3 style='color: #333; margin: 0;'>🎉✨ **Join the Fun!** ✨🎉<br>
        🚀 Sign up or sign in to access ALL videos 🎬 and unlock exclusive features! 💥 Let's get started! 🔓🎉</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Display logo and heading
    header_col1, header_col2 = st.columns([1, 8])
    with header_col1:
        st.image("logo.jpeg", width=60)  # Adjust width as needed
    with header_col2:
        st.title("Welcome to Sparkplay")
    # Define video_urls before using it
    video_urls = [
        "Videos_Data/video_52.mp4",
        "Videos_Data/video_42.mp4",
        "Videos_Data/video_13.mp4",
    ]

#     import random

# # Random video picker
#     if st.button("Surprise Me!", key="surprise_me_button"):
#         video_urls = [
#             "Videos_Data/video_51.mp4",
#             "Videos_Data/video_41.mp4",
#             "Videos_Data/video_36.mp4",
#     ]
#     random_video = random.choice(video_urls)
#     st.video(random_video)

    # Featured Videos Section
    st.subheader("Explore by Genre")

    # Action Videos Section
    st.write("Action Videos")
    action_video_urls = [
        "Videos_Data/video_11.mp4",
        "Videos_Data/video_12.mp4",
        "Videos_Data/video_13.mp4",
    ]
    action_cols = st.columns(3)
    for i, url in enumerate(action_video_urls):
        with action_cols[i]:
            st.video(url)
            st.caption(f"Action Video {i+1}")

    # Comedy Videos Section
    st.write("Comedy Videos")
    comedy_video_urls = [
        "Videos_Data/video_21.mp4",
        "Videos_Data/video_22.mp4",
        "Videos_Data/video_24.mp4",
    ]
    comedy_cols = st.columns(3)
    for i, url in enumerate(comedy_video_urls):
        with comedy_cols[i]:
            st.video(url)
            st.caption(f"Comedy Video {i+1}")

    # Music Videos Section
    st.write("Music Videos")
    music_video_urls = [
        "Videos_Data/video_6.mp4",
        "Videos_Data/video_3.mp4",
        "Videos_Data/video_10.mp4",
    ]
    music_cols = st.columns(3)
    for i, url in enumerate(music_video_urls):
        with music_cols[i]:
            st.video(url)
            st.caption(f"Music Video {i+1}")
    
    import random
    st.subheader("Ready for a Surprise? Let’s Watch Something Fun!")

# Random video picker
    if st.button("Surprise Me!", key="surprise_me_button"):
        video_urls = [
            "Videos_Data/video_51.mp4",
            "Videos_Data/video_52.mp4",
            "Videos_Data/video_41.mp4",
            "Videos_Data/video_52.mp4",
            "Videos_Data/video_36.mp4",
            "Videos_Data/video_31.mp4",
            "Videos_Data/video_21.mp4",
            "Videos_Data/video_11.mp4",
            "Videos_Data/video_10.mp4",
            "Videos_Data/video_13.mp4",
    ]
    random_video = random.choice(video_urls)
    st.video(random_video)

    # FAQ Section
    st.subheader("Frequently Asked Questions")
    with st.expander("🔶Why Should I Sign Up?"):
        st.write("""
        Signing up allows you to unlock premium features such as:
        * *Personalized Recommendations:* Get video suggestions tailored to your interests. 
        * *Watch History Tracking:* Never lose track of your favorite videos.
        * *Community Features:* Like, comment, share videos and chat with friends.""")
    with st.expander("🔶What is SparkPlay?"):
        st.write("""
        *SparkPlay* is a cutting-edge video recommendation platform that helps you:
        - Discover new and trending videos
        - Get recommendations
        - Engage with a small vibrant community of video lovers
        """)
    with st.expander("🔶What are your features?"):
        st.write("""
        - ✅ *Personalized Video Recommendations*: AI-based suggestions to enhance your experience.
        - 📺 *Track Your Watch History*: Save and revisit your favorite content.
        - ❤️ *Like and Comment on Videos*: Interact with content and engage with the community.
        - 🔄 *Upload  and Share Videos*:  Share your videos.
        - 💬 *Chat with Other Users*: Join discussions and connect with video lovers
        """)
    with st.expander("🔶How do I Sign Up?"):
        st.write("""
        Signing up is quick and easy! Follow these steps:
        1. Click on the *Sign Up* button at the top-right corner of the homepage.
        2. Fill out the form with your details.
        4. Verify your email through the top sent to your email.
        5. Log in and start exploring personalized video content!
        """)
    with st.expander("🔶Need More Help?"):
        st.write(
        """
        If you have additional questions or need technical support:
        - 📧 *Need help? Contact us at [sparkplay4@gmail.com]*
        - ⏳ Please allow 1-3 business days for us to get back to you.
        """
        )

# Fetch user_ids dynamically
user_ids = fetch_user_ids()

# Personalized dashboard for logged-in users
if st.session_state.logged_in:
    if "developer" in st.session_state.username.lower():
        developer_dashboard(st.session_state.username)
    elif "data_analyst" in st.session_state.username.lower():
        data_analyst_dashboard(st.session_state.username)
    elif "product_manager" in st.session_state.username.lower():
        product_manager_dashboard(st.session_state.username)
    elif "advertiser" in st.session_state.username.lower():
        advertiser_dashboard(st.session_state.username)
    elif "system_admin" in st.session_state.username.lower():
        system_administrator_dashboard(st.session_state.username)
    elif "admin" in st.session_state.username.lower():
        admin_dashboard(st.session_state.username)
    else:
        # Display logo and heading
        header_col1, header_col2 = st.columns([1, 8])
        with header_col1:
            st.image("logo.jpeg", width=60)  # Adjust width as needed
        with header_col2:
            st.title("Welcome to Sparkplay")

        st.title(f"Welcome, {st.session_state.username}!")

        # Section to display newly uploaded videos
        if "new_uploaded_videos" in st.session_state and st.session_state.new_uploaded_videos:
            st.subheader("Newly Uploaded Videos")
            new_video_cols = st.columns(3)  # Create columns for layout
            for i, video in enumerate(st.session_state.new_uploaded_videos):
                with new_video_cols[i % 3]:
                    st.video(video["Path"])  # Display video
                    st.caption(f"{video['Title']} ({video['Category']})")

        # Function to fetch user activity
        def fetch_user_activity(username):
            """Fetch activity data for the given user."""
            if os.path.exists(USER_ACTIVITY_FILE):
                with open(USER_ACTIVITY_FILE, "r") as file:
                    user_activity = json.load(file)
                return user_activity.get(username, {})
            return {}

        # Sidebar for chat toggle and chat recipient selection
        st.sidebar.subheader("Options")
        if "show_chat" not in st.session_state:
            st.session_state.show_chat = False  # Track chat window state

        # History button
        if st.sidebar.button("History", key="history_button"):
            st.subheader("Watch History")

            # Fetch user activity for the logged-in user
            user_activity = fetch_user_activity(st.session_state.username)

            if "viewed" in user_activity and user_activity["viewed"]:
                for video_id in user_activity["viewed"]:
                    video_path = f"Videos_Data/{video_id}.mp4"  # Adjust the path based on your structure
                    st.video(video_path)
                    st.caption(f"Watched: {video_id}")
            else:
                st.write("No videos in history yet.")

        # Liked Videos button
        if st.sidebar.button("Liked Videos", key="liked_videos_button"):
            st.subheader("Liked Videos")

            # Fetch user activity for the logged-in user
            user_activity = fetch_user_activity(st.session_state.username)

            if "liked" in user_activity and user_activity["liked"]:
                for video_id in user_activity["liked"]:
                    video_path = f"Videos_Data/{video_id}.mp4"  # Adjust the path based on your structure
                    if os.path.exists(video_path):
                        st.video(video_path)
                        st.caption(f"Liked: {video_id}")
                    else:
                        st.error(f"Video {video_id} not found.")
            else:
                st.write("No liked videos yet.")

        toggle_chat = st.sidebar.button("Toggle Chat")  # Button to open/close chat
        if toggle_chat:
            st.session_state.show_chat = not st.session_state.show_chat

        st.sidebar.subheader("Chat")
        all_users = [user for user in fetch_user_ids() if user != st.session_state.username]
        recipient = st.sidebar.selectbox("Select a user to chat with:", all_users, key="recipient_selector")

        # Main layout: Video, Recommendations, and optionally Chat
        video_col, chat_col = st.columns([4, 1])

        with video_col:
            if st.session_state.current_video:
                # Display the selected video
                st.video(f"Videos_Data/{st.session_state.current_video}.mp4")
                st.caption(f"Currently Watching: {st.session_state.current_video}")

                # Update history and interactions
                if st.session_state.current_video not in st.session_state.history:
                    st.session_state.history.append(st.session_state.current_video)
                st.session_state.user_interactions.append({"User_ID": st.session_state.username, "Video_ID": st.session_state.current_video, "Interaction_Type": "view"})
                track_view(st.session_state.username, st.session_state.current_video)

                # Interaction buttons
                col1, col2, col3, col4 = st.columns([1, 1, 1, 6])
                with col1:
                    if st.button("👍 Like"):
                        update_like(st.session_state.username, st.session_state.current_video)
                        st.experimental_set_query_params(rerun="true")
                with col2:
                    if st.button("👎 Dislike"):
                        update_dislike(st.session_state.username, st.session_state.current_video)
                        st.experimental_set_query_params(rerun="true")
                with col3:
                    if st.button("🔗 Share"):
                        share_video(st.session_state.username, st.session_state.current_video)
                        st.success("Video shared!")
                with col4:
                    comment_text = st.text_input("Add a comment", key="comment_input")
                    if st.button("Post Comment"):
                        if comment_text.strip():
                            add_comment(st.session_state.username, st.session_state.current_video, comment_text)
                            st.success("Comment added!")
                        else:
                            st.error("Comment cannot be empty!")

                # Display recommended videos
                if offline_mode:
                    # Use cached data for recommendations
                    recommendations = recommend_videos_cf(st.session_state.username)
                else:
                    # Use live data for recommendations
                    interaction_matrix = create_interaction_matrix(st.session_state.user_interactions, video_metadata, user_ids)
                    recommendations = recommend_videos_cf(st.session_state.username, interaction_matrix, video_metadata, user_ids)

                st.subheader("Recommended Videos")
                recommended_cols = st.columns(3)
                for i, video in enumerate(recommendations):
                    with recommended_cols[i % 3]:
                        st.video(video["Path"])
                        st.caption(video["Title"])
                        if st.button(f"Play {video['Title']}", key=f"play_{video['Video_ID']}"):
                            st.session_state.current_video = video["Video_ID"]
                            st.experimental_set_query_params(rerun="true")
            else:
                # Show all videos
                st.subheader("All Videos")
                video_cols = st.columns(3)
                for i, video in enumerate(video_metadata):
                    with video_cols[i % 3]:
                        st.video(video["Path"])
                        st.caption(video["Title"])
                        if st.button(f"Play {video['Title']}", key=f"play_{video['Video_ID']}"):
                            st.session_state.current_video = video["Video_ID"]
                            st.experimental_set_query_params(rerun="true")
        import random
        st.subheader("Can't choose? Let us surprise you with your next favorite video!")

        # Define video_urls at the beginning of your script
        video_urls = [
            "Videos_Data/video_1.mp4",
            "Videos_Data/video_2.mp4",
            "Videos_Data/video_3.mp4",
            "Videos_Data/video_4.mp4",
            "Videos_Data/video_5.mp4",
            "Videos_Data/video_6.mp4",
            "Videos_Data/video_7.mp4",
            "Videos_Data/video_8.mp4",
            "Videos_Data/video_9.mp4",
            "Videos_Data/video_10.mp4",
        ]

# Later in your code, you can use it
        if st.button("Surprise Me!", key="surprise_me_button"):
            random_video = random.choice(video_urls)
            st.video(random_video)
        # Chat section
        if st.session_state.show_chat and recipient:
            with chat_col:
                st.subheader(f"Chat with {recipient}")

                # Fetch chat messages
                messages = fetch_user_chat(st.session_state.username, recipient)
                st.divider()
                st.write("Messages:")
                for msg in messages:
                    st.markdown(f"**{msg['sender']}**: {msg['message']} (_{msg['timestamp']}_)")

                # Input for new message
                new_message = st.text_input("Type your message", key="new_message_input")
                if st.button("Send", key="send_message_button"):
                    if new_message.strip():
                        send_user_message(st.session_state.username, recipient, new_message)
                        st.experimental_set_query_params(rerun="true")
                    else:
                        st.error("Message cannot be empty!")

# Footer
st.write("---")
st.write("Powered by Streamlit")
