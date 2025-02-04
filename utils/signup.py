import streamlit as st
from user_auth import sign_up

st.title("Sign Up")

username = st.text_input("Username")
password = st.text_input("Password", type="password")
confirm_password = st.text_input("Confirm Password", type="password")

if st.button("Sign Up"):
    if password != confirm_password:
        st.error("Passwords do not match.")
    elif sign_up(username, password):
        st.success("Sign up successful! You can now log in.")
    else:
        st.error("Username already exists. Please choose a different username.")
