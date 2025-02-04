import streamlit as st

def product_manager_dashboard(username):
    """Product Manager Dashboard."""
    st.title(f"Welcome, {username}! (Product Manager)")

    # Review User Engagement Trends
    st.header("Review User Engagement Trends")
    st.line_chart({"Watch Time (hrs)": [10, 12, 14, 16, 15], "CTR (%)": [5, 6, 8, 10, 9]})
    st.write("Analyze trends in user engagement over the past week.")

    # Analyze Feature Feedback
    st.header("Analyze Feature Feedback")
    feature_feedback = {
        "Recommendation Engine": 4.5,
        "UI/UX Design": 3.8,
        "New Features": 4.2,
    }
    st.write("Feature Ratings:")
    for feature, rating in feature_feedback.items():
        st.write(f"{feature}: {rating}/5")

    # Prioritize Features Based on User Needs
    st.header("Prioritize Features Based on User Needs")
    priorities = ["Improved Recommendations", "Enhanced UI", "New Content Categories"]
    selected_priority = st.selectbox("Select a feature to prioritize:", priorities)
    st.write(f"You selected: {selected_priority}")
    if st.button("Set Priority"):
        st.success(f"'{selected_priority}' has been prioritized!")

    # Track Feature Performance After Deployment
    st.header("Track Feature Performance After Deployment")
    st.metric("Feature X Engagement", "85%", delta="2% Increase")
    st.metric("Feature Y Clicks", "1200", delta="200 Increase")
    st.metric("Feature Z Issues", "3", delta="-1 Decrease")

    # Logout option
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.experimental_rerun()
