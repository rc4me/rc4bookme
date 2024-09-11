import streamlit as st
from streamlit_calendar import calendar
from datetime import timedelta, datetime
import pytz
from typing import List

st.set_page_config("RC4ME - Book", layout="wide", page_icon="resources/rc4meLogo.jpg")

from utils import validations
from backend import menu
import backend.submitBookings as backend


# st.json(st.session_state, expanded=False)
menu.redirectIfUnauthenticated()
menu.displayMenu()

calendarOptions = backend.getCalendarOptions()
if st.session_state["calendar"]["allBookingsCache"] is None:
    backend.updateAllBookingsCache()

st.header("TR3 availability")
if (
    st.button("Refresh calendar")
    or st.session_state["calendar"]["allBookingsCache"] is None
):
    with st.spinner("Getting bookings..."):
        backend.updateAllBookingsCache()
mycalendar = calendar(
    st.session_state["calendar"]["allBookingsCache"], options=calendarOptions
)


st.subheader("Submit bookings")
now = datetime.now(pytz.timezone("Singapore")).replace(minute=0, second=0)
startDate = st.date_input("### Start date", value=now.date() + timedelta(days=2))
startTime = st.time_input("### Start time", step=timedelta(hours=0.5), value=now.time())
endDate = st.date_input(
    "### End date", value=startDate + timedelta(days=2), min_value=startDate
)
endTime = st.time_input(
    "### End time",
    step=timedelta(hours=0.5),
    value=(now + timedelta(hours=2)).time(),
)
friendList: List = st.session_state["bookingForm"]["friendIds"]
newId = st.text_input("Student ID of your friends using TR3 with you:")
colA, colB = st.columns([1, 1])
with colA:
    if st.button("Add"):
        if not validations.isValidStudentId(newId):
            st.warning("Invalid student ID")
        elif newId.upper() in friendList:
            st.warning("Student ID already in list")
        elif newId.upper() == st.session_state["studentId"]:
            st.warning("Cannot add yourself into friends list")
        else:
            friendList.append(newId.upper())
with colB:
    if st.button("Reset"):
        friendList.clear()
if len(friendList) != 0:
    st.dataframe({"Student ID": friendList}, use_container_width=True)


if st.button("Submit", type="primary"):
    try:
        startTs, endTs = backend.getBookingTs(startDate, endDate, startTime, endTime)
        with st.spinner("Processing booking..."):
            backend.tryInsertBooking(
                startTs,
                endTs,
                st.session_state["userInfo"]["studentId"],
                st.session_state["userInfo"]["teleHandle"],
                st.session_state["userInfo"]["name"],
                friendIds=friendList,
            )
        st.info("Booking submitted!")
    except ValueError as e:
        st.warning(str(e))
