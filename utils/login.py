import streamlit as st
from user_auth import login

st.title("Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if login(username, password):
        st.success("Login successful!")
        # Redirect or add logic to navigate to the main app after login
    else:
        st.error("Invalid username or password.")
