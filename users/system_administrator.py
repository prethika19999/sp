import streamlit as st
import psutil
import time

def system_administrator_dashboard(username):
    """System Administrator Dashboard."""
    st.title(f"Welcome, {username}! (System Administrator)")

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

    # Logout option
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.experimental_rerun()
