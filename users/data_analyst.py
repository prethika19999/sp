import streamlit as st

def data_analyst_dashboard(username):
    """Data Analyst Dashboard."""
    st.title(f"Welcome, {username}! (Data Analyst)")

    # Analyze User Behavior
    st.header("Analyze User Behavior (Watch Time, CTR, etc.) Metrics")
    watch_time = st.slider("Average Watch Time (mins)", min_value=0, max_value=60, value=30)
    click_through_rate = st.slider("Click Through Rate (CTR)", min_value=0.0, max_value=1.0, step=0.01, value=0.45)
    st.write(f"Average Watch Time: {watch_time} mins")
    st.write(f"Click Through Rate (CTR): {click_through_rate * 100}%")

    # Test Algorithm Adjustments (A/B Testing)
    st.header("Test Algorithm Adjustments (A/B Testing)")
    test_variants = st.radio("Choose Test Variant", ["Variant A", "Variant B"])
    st.write(f"Running A/B test for: {test_variants}")
    if st.button("Run A/B Test"):
        st.success(f"A/B Test for {test_variants} completed successfully!")

    # Improve Recommendation Accuracy
    st.header("Improve Recommendation Accuracy")
    st.write("Monitor and fine-tune recommendation models based on the analyzed metrics.")
    st.metric(label="Current Recommendation Accuracy", value="92%")
    st.metric(label="Target Recommendation Accuracy", value="95%")

    # Track Engagement
    st.header("Track Engagement")
    st.write("View engagement metrics such as likes, comments, shares.")
    st.metric(label="Total Engagement", value="1500 interactions")

    # Logout option
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.experimental_rerun()
