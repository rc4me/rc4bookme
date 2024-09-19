import streamlit as st
from helpers import menu

menu.redirectIfUnauthenticated()
st.session_state["userInfo"].clear()
st.session_state["isLoggedIn"] = False
st.session_state["isRegisteredUser"] = False
st.switch_page("main.py")
