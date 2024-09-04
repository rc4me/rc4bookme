import streamlit as st

from streamlit_google_auth import Authenticate
from oauthlib.oauth2 import InvalidGrantError

st.set_page_config("RC4ME - Login", layout="wide", page_icon="resources/rc4meLogo.jpg")

from backend import menu, database
from backend import main as backend


menu.displayMenu()
st.json(st.session_state, expanded=False)
st.title("RC4ME - Login")


authenticator = Authenticate(
    secret_credentials_path="resources/oauth_credentials.json",
    cookie_name=st.secrets["LOGIN_COOKIE"],
    cookie_key=st.secrets["LOGIN_COOKIE_KEY"],
    redirect_uri="http://localhost:8501",
)


def logoutUser():
    authenticator.logout()


with st.spinner():
    while True:
        try:
            authenticator.check_authentification()
            break
        except InvalidGrantError:
            pass

authenticator.login(justify_content="left", color="white")
if not st.session_state.get("connected", False):
    st.stop()

# st.image(st.session_state["user_info"].get("picture"))
# st.write(f"Hello, {st.session_state['user_info'].get('name')}")
# st.write(f"Your email is {st.session_state['user_info'].get('email')}")

with st.spinner("Verifying account..."):
    st.session_state["isRegisteredUser"] = database.isRegisteredUser(
        st.session_state["user_info"]["email"]
    )

if not st.session_state["isRegisteredUser"]:
    st.header(
        f"Hi {st.session_state["user_info"]["name"]}, looks like it's your first time here!"
    )
    st.subheader("Just key in a few details for us:")
    studentId = st.text_input("Student ID (eg. `E1234567`)")
    teleHandle = st.text_input("Telegram handle")
    gradYear = st.number_input("Year of graduation", min_value=2025, value=None)
    if st.button(
        "Register",
        type="primary",
        disabled=not backend.isValidStudentId(studentId)
        or teleHandle is None
        or gradYear is None,
    ):
        with st.spinner("Registering..."):
            database.registerStudent(
                studentId, teleHandle, st.session_state["user_info"], gradYear
            )
        st.session_state["isRegisteredUser"] = True
        st.rerun()

if st.session_state["isRegisteredUser"] and st.session_state["connected"]:
    st.session_state["studentId"] = database.getStudentId(
        st.session_state["user_info"]["email"]
    )
    st.switch_page("pages/bookTr3.py")
