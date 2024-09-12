import streamlit as st
from streamlit_calendar import calendar
from datetime import timedelta, datetime
import pytz
from typing import List, Dict

st.set_page_config("RC4ME - Book", layout="wide", page_icon="resources/rc4meLogo.jpg")

from utils import validations
from backend import menu
import backend.submitBookings as backend

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
calendarEvent: Dict = calendar(
    st.session_state["calendar"]["allBookingsCache"], options=calendarOptions
)
if calendarEvent.get("callback", "") == "eventClick":
    st.toast(calendarEvent["eventClick"]["event"]["title"])


st.subheader("Submit bookings")
defaultStart = datetime.now(pytz.timezone("Singapore")).replace(
    minute=0, second=0
) + timedelta(days=2)
startDate = st.date_input(
    "### Start date",
    value=defaultStart.date(),
    min_value=datetime.now(pytz.timezone("Singapore")).date(),
)
startTime = st.time_input("### Start time", step=timedelta(hours=0.5), value=None)
startTs = (
    None
    if startTime is None
    else pytz.timezone("Singapore").localize(datetime.combine(startDate, startTime))
)

defaultEnd = None if startTs is None else startTs + timedelta(hours=2)
endDate = st.date_input(
    "### End date",
    min_value=startDate,
    value=None if defaultEnd is None else defaultEnd.date(),
)
endTime = st.time_input(
    "### End time",
    step=timedelta(hours=0.5),
    value=None if defaultEnd is None else defaultEnd.time(),
)
endTs = (
    None
    if (endDate is None or endTime is None)
    else pytz.timezone("Singapore").localize(datetime.combine(endDate, endTime))
)

friendList: List = st.session_state["bookingForm"]["friendIds"]
allUsers = backend.getAllUsers()
friends = st.multiselect("Booking used with:", options=allUsers, placeholder="Enter names...")
friendIds = [allUsers[friend] for friend in friends]

if st.button("Submit", type="primary", disabled=endTs is None or startTs is None):
    try:
        validations.verifyBookingPeriod(startTs, endTs)
        with st.spinner("Processing booking..."):
            backend.tryInsertBooking(
                startTs,
                endTs,
                st.session_state["userInfo"]["studentId"],
                st.session_state["userInfo"]["teleHandle"],
                st.session_state["userInfo"]["name"],
                friendIds=friendIds,
            )
        st.info("Booking submitted!")
    except ValueError as e:
        st.warning(str(e))
