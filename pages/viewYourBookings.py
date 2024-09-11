import streamlit as st
from streamlit_calendar import calendar

st.set_page_config(
    "RC4ME - View Bookings", layout="wide", page_icon="resources/rc4meLogo.jpg"
)

import backend.viewYourBookings as backend
from backend import menu

menu.redirectIfUnauthenticated()
menu.displayMenu()

calendarsState = st.session_state["calendar"]
studentId = st.session_state["userInfo"]["studentId"]

st.title("View bookings")

if st.session_state["calendar"]["userBookingsCache"] is None or st.button(
    "Refresh calendar"
):
    with st.spinner("Getting bookings..."):
        backend.updateUserBookingsCache(studentId)

calendarOptions = backend.getCalendarOptions()
mycalendar = calendar(
    st.session_state["calendar"]["userBookingsCache"], options=calendarOptions
)
