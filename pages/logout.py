import streamlit as st

st.set_page_config("RC4ME - Logout", layout="wide", page_icon="resources/rc4meLogo.png")
st.session_state.clear()
st.switch_page("main.py")
