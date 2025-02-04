import streamlit as st

def content_creator_page():
    st.title("Content Creator Dashboard")

    # User Authentication
    st.subheader("Login")
    email = st.text_input("Email", key="email_input")
    password = st.text_input("Password", type="password", key="password_input")
    if st.button("Login"):
        if email == "creator@example.com" and password == "password123":  # Replace with actual authentication
            st.session_state["logged_in_creator"] = True
            st.success("Logged in successfully!")
        else:
            st.error("Invalid email or password.")

    if "logged_in_creator" in st.session_state and st.session_state["logged_in_creator"]:
        # Content Upload
        st.subheader("Upload New Content")
        uploaded_file = st.file_uploader("Choose a file", type=["mp4", "mov", "avi"])
        if uploaded_file:
            st.success("File uploaded successfully!")
            st.video(uploaded_file)  # Optional preview

        # View Metrics
        st.subheader("View Video Performance Metrics")
        st.write("Sample Metrics for your uploaded videos:")
        metrics = {
            "Video 1": {"Views": 1200, "Likes": 300, "Engagement": "75%"},
            "Video 2": {"Views": 800, "Likes": 150, "Engagement": "60%"}
        }
        for video, data in metrics.items():
            st.write(f"**{video}:** Views: {data['Views']}, Likes: {data['Likes']}, Engagement: {data['Engagement']}")

        # Analyze Metrics
        st.subheader("Analyze Metrics")
        st.write("Analysis based on video performance:")
        st.write("- Video 1 is performing better than Video 2.")
        st.write("- Engagement is high for Video 1, optimize content for similar performance.")

        # Optimize Future Uploads
        st.subheader("Optimize Future Uploads")
        st.write("Recommendations:")
        st.write("- Keep videos under 5 minutes for better engagement.")
        st.write("- Post consistently every week.")

        # Logout
        if st.button("Logout"):
            st.session_state["logged_in_creator"] = False
            st.success("Logged out successfully!")
