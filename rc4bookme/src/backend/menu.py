import streamlit as st


def redirectIfUnauthenticated():
    isAuthenticated = st.session_state.get("connected", False) and st.session_state.get(
        "isRegisteredUser", False
    )
    if not isAuthenticated:
        st.switch_page("main.py")


def displayMenu():
    isAuthenticated = st.session_state.get("connected", False) and st.session_state.get(
        "isRegisteredUser", False
    )
    if isAuthenticated:
        st.sidebar.page_link("pages/bookTr3.py", label="Book TR3")
        st.sidebar.page_link("pages/profile.py", label="Profile")
    else:
        st.sidebar.page_link("main.py", label="Login")
    st.sidebar.page_link("pages/logout.py", label="Logout")