import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime, time

st.set_page_config("RC4ME - Login", layout="wide", page_icon="resources/rc4meLogo.jpg")

from backend import menu, database
import backend.bookTr3 as backend


st.json(st.session_state, expanded=False)
menu.redirectIfUnauthenticated()
menu.displayMenu()

calendar_options = backend.getCalendarOptions()
calendar_events = [
    {
        "title": "Event 1",
        "start": datetime(2024, 9, 4, 15, 0, 0).timestamp() * 1000,
        "end": datetime(2024, 9, 4, 19, 0, 0).timestamp() * 1000,
        "resourceId": "a",
    },
]

st.header("TR3 availability")
mycalendar = calendar(events=calendar_events, options=calendar_options)

st.subheader("Submit bookings")
with st.form("bookingDetails"):
    col1, col2 = st.columns(2)
    minDate, maxDate = backend.getValidDateRange()
    with col1:
        startDate = st.date_input(
            "### Start date", min_value=minDate, max_value=maxDate
        )
        endDate = st.date_input(
            "### End date", min_value=minDate, max_value=maxDate
        )
    with col2:
        startTime = st.time_input("### Start time")
        endTime = st.time_input("### End time")
       
    if st.form_submit_button("Submit", type="primary"):
        try:
            startTs, endTs = backend.getDatetime(startDate, endDate, startTime, endTime)
            
        except ValueError:
            st.warning("End time cannot be earlier than start time")