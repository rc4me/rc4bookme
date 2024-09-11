import streamlit as st

st.set_page_config("RC4ME - Login", layout="wide", page_icon="resources/rc4meLogo.jpg")

from backend import menu, database, auth
from utils import validations, states

menu.redirectIfAuthenticated()
menu.displayMenu()

st.title("RC4ME - Login")

states.setState("bookingForm", {"friendIds": []})
states.setState(
    "db",
    {"bookings": None, "users": None},
)
states.setState("calendar", {"allBookingsCache": None, "userBookingsCache": None})
states.setState("userInfo", {})
states.setState("isLoggedIn", False)
states.setState("isRegisteredUser", None)

st.json(st.session_state, expanded=False)

if st.session_state["userInfo"].get("email", None) is None:
    st.session_state["userInfo"]["email"] = auth.getUserEmail()
st.session_state["isLoggedIn"] = st.session_state["userInfo"]["email"] is not None

if not st.session_state["isLoggedIn"]:
    auth.displayLoginButton()
    st.stop()

if st.session_state["isRegisteredUser"] is None:
    with st.spinner("Verifying account..."):
        st.session_state["isRegisteredUser"] = database.isRegisteredUser(
            st.session_state["userInfo"]["email"]
        )

if not st.session_state["isRegisteredUser"]:
    st.header("Hi, looks like it's your first time here!")
    st.subheader("Just key in a few details for us:")
    name = st.text_input("Full name (as in matriculation card)")
    studentId = st.text_input("Student ID (eg. `E1234567`)")
    teleHandle = st.text_input("Telegram handle")
    gradYear = st.number_input("Year of graduation", min_value=2025, value=None)
    if st.button(
        "Register",
        type="primary",
        disabled=not validations.isValidStudentId(studentId)
        or teleHandle is None
        or gradYear is None,
    ):
        try:
            with st.spinner("Registering..."):
                if database.isAlreadyRegistered(studentId, teleHandle):
                    raise ValueError(
                        "Your Telegram handle / Student ID is already registered."
                    )
                database.registerStudent(
                    studentId,
                    teleHandle,
                    st.session_state["userInfo"]["email"],
                    name,
                    gradYear,
                )
            st.session_state["isRegisteredUser"] = True
            st.session_state["userInfo"].update(
                database.getUserDetails(st.session_state["userInfo"]["email"])
            )
            st.rerun()
        except ValueError as e:
            st.warning(str(e))

if st.session_state["isRegisteredUser"] and st.session_state["isLoggedIn"]:
    st.session_state["userInfo"].update(
        database.getUserDetails(st.session_state["userInfo"]["email"])
    )
    st.switch_page("pages/submitBookings.py")
