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

if calendarsState["userBookingsRange"] is None:
    calendarsState["userBookingsRange"] = backend.getDefaultDateRange()
if calendarsState["userBookingsCache"] is None:
    backend.updateUserBookingsCache(studentId, *calendarsState["userBookingsRange"])

st.title("View bookings")

col1, col2 = st.columns([5, 1])

with col1:
    if st.button("Refresh calendar"):
        backend.updateUserBookingsCache(studentId, *calendarsState["userBookingsRange"])

with col2:
    with st.popover("Filter by date"):
        startDate = st.date_input("From:")
        endDate = st.date_input("To:")
        if st.button("Apply", type="primary"):
            calendarsState["userBookingsRange"] = (startDate, endDate)
            backend.updateUserBookingsCache(studentId, *calendarsState["userBookingsRange"])


calendarOptions = backend.getCalendarOptions()
mycalendar = calendar(
    st.session_state["calendar"]["userBookingsCache"], options=calendarOptions
)
