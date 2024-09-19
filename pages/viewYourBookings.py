import streamlit as st
from streamlit_calendar import calendar

st.set_page_config(
    "RC4ME - View Bookings", layout="wide", page_icon="resources/rc4meLogo.png"
)

import helpers.viewYourBookings as helpers
from helpers import menu

menu.redirectIfUnauthenticated()
menu.displayMenu()

calendarsState = st.session_state["calendar"]
studentId = st.session_state["userInfo"]["studentId"]

st.title("View bookings")

if (
    st.session_state["calendar"]["userBookingsCache"] is None
    or st.button("Refresh calendar")
    or st.session_state["atPage"] != "viewYourBookings"
):
    st.session_state["atPage"] = "viewYourBookings"
    with st.spinner("Getting bookings..."):
        helpers.updateUserBookingsCache(studentId)

calendarOptions = helpers.getCalendarOptions()
mycalendar = calendar(
    st.session_state["calendar"]["userBookingsCache"], options=calendarOptions
)
