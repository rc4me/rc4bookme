import streamlit as st
from helpers import auth

st.set_page_config("RC4ME - Logout", layout="wide", page_icon="resources/rc4meLogo.png")

# Clear the login cookie
auth.clearUserSession()

st.session_state.clear()
st.switch_page("main.py")
