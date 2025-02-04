import streamlit as st

def advertiser_dashboard(username):
    """Advertiser Dashboard."""
    st.title(f"Welcome, {username}! (Advertiser)")

    # Access User Demographics and Preferences
    st.header("Access User Demographics and Preferences")
    demographics = {
        "Age Groups": [18, 24, 30, 40, 50],
        "Preferences": ["Technology", "Fashion", "Gaming", "Fitness", "Travel"],
    }
    st.write("User Demographics:")
    st.bar_chart({"Age Groups": demographics["Age Groups"]})
    st.write("Top Preferences:")
    for pref in demographics["Preferences"]:
        st.markdown(f"- {pref}")

    # Monitor Ad Engagement
    st.header("Monitor Ad Engagement (CTR, Impressions)")
    engagement_metrics = {"CTR (%)": [5.5, 6.2, 7.1, 8.0], "Impressions (k)": [20, 25, 28, 30]}
    st.line_chart(engagement_metrics)

    # Place Ads Strategically
    st.header("Place Ads Strategically")
    ad_locations = ["Homepage Banner", "Sidebar", "Video Pre-roll", "Search Results"]
    selected_location = st.selectbox("Select Ad Placement Location:", ad_locations)
    st.write(f"Selected Location: {selected_location}")
    if st.button("Place Ad"):
        st.success(f"Ad successfully placed on {selected_location}!")

    # Optimize Future Ad Placements
    st.header("Optimize Future Ad Placements")
    st.metric("CTR Improvement", "8%", delta="2% Increase")
    st.metric("Ad Spend Efficiency", "85%", delta="5% Increase")
    st.metric("Impressions", "30k", delta="5k Increase")

    # Logout option
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.experimental_rerun()
