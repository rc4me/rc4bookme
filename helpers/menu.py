import streamlit as st
from helpers import auth, database
from utils import states
import helpers.main as helpers_main


def _ensureSessionInitialized():
    """Ensure session state is initialized and restore from cookie if needed."""
    # Initialize session states if not done
    if "userInfo" not in st.session_state:
        helpers_main.initialiseSessionStates()

    # Try to restore login from cookie if not logged in
    if not st.session_state.get("isLoggedIn", False):
        email = auth.getUserEmail()
        if email:
            st.session_state["userInfo"]["email"] = email
            st.session_state["isLoggedIn"] = True
            # Check if registered and load user details
            if database.isRegisteredUser(email):
                st.session_state["isRegisteredUser"] = True
                st.session_state["userInfo"].update(database.getUserDetails(email))


def redirectIfUnauthenticated():
    _ensureSessionInitialized()
    isAuthenticated = st.session_state.get(
        "isLoggedIn", False
    ) and st.session_state.get("isRegisteredUser", False)
    if not isAuthenticated:
        st.switch_page("main.py")


def redirectIfAuthenticated():
    _ensureSessionInitialized()
    isAuthenticated = st.session_state.get(
        "isLoggedIn", False
    ) and st.session_state.get("isRegisteredUser", False)
    if isAuthenticated:
        st.switch_page("pages/submitBookings.py")


def redirectIfNotAdmin():
    _ensureSessionInitialized()
    isAuthenticated = st.session_state.get(
        "isLoggedIn", False
    ) and st.session_state.get("isRegisteredUser", False)
    if not isAuthenticated:
        st.switch_page("main.py")
        return
    if st.session_state["userInfo"].get("userType") != "admin":
        st.switch_page("pages/submitBookings.py")


def displayMenu():
    isAuthenticated = st.session_state.get(
        "isLoggedIn", False
    ) and st.session_state.get("isRegisteredUser", False)
    if isAuthenticated:
        st.sidebar.header(f'Welcome, {st.session_state["userInfo"].get("name", "User")}')
        st.sidebar.page_link("pages/submitBookings.py", label="Submit bookings")
        st.sidebar.page_link("pages/viewYourBookings.py", label="View your bookings")
        if st.session_state["userInfo"].get("userType") == "admin":
            st.sidebar.page_link("pages/adminView.py", label="Admin view")
    else:
        st.sidebar.page_link("main.py", label="Login")
    st.sidebar.page_link("pages/logout.py", label="Logout")
