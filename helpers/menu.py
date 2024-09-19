import streamlit as st


def redirectIfUnauthenticated():
    isAuthenticated = st.session_state.get(
        "isLoggedIn", False
    ) and st.session_state.get("isRegisteredUser", False)
    if not isAuthenticated:
        st.switch_page("main.py")


def redirectIfAuthenticated():
    isAuthenticated = st.session_state.get(
        "isLoggedIn", False
    ) and st.session_state.get("isRegisteredUser", False)
    if isAuthenticated:
        st.switch_page("pages/submitBookings.py")


def redirectIfNotAdmin():
    isAuthenticated = st.session_state.get(
        "isLoggedIn", False
    ) and st.session_state.get("isRegisteredUser", False)
    if not isAuthenticated:
        st.switch_page("main.py")
        return
    if st.session_state["userInfo"]["userType"] != "admin":
        st.switch_page("pages/submitBookings.py")


def displayMenu():
    isAuthenticated = st.session_state.get(
        "isLoggedIn", False
    ) and st.session_state.get("isRegisteredUser", False)
    if isAuthenticated:
        st.sidebar.header(f'Welcome, {st.session_state["userInfo"]["name"]}')
        st.sidebar.page_link("pages/submitBookings.py", label="Submit bookings")
        st.sidebar.page_link("pages/viewYourBookings.py", label="View your bookings")
        if st.session_state["userInfo"]["userType"] == "admin":
            st.sidebar.page_link("pages/adminView.py", label="View all bookings")
    else:
        st.sidebar.page_link("main.py", label="Login")
    st.sidebar.page_link("pages/logout.py", label="Logout")
