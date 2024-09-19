import streamlit as st
from streamlit_calendar import calendar
from datetime import timedelta, datetime
import pytz
from typing import List, Dict

st.set_page_config("RC4ME - Book", layout="wide", page_icon="resources/rc4meLogo.jpg")

from utils import validations
from helpers import menu
import helpers.submitBookings as helpers

menu.redirectIfUnauthenticated()
menu.displayMenu()

st.header("TR3 availability")
if (
    st.button("Refresh calendar")
    or st.session_state["calendar"]["allBookingsCache"] is None
    or st.session_state["atPage"] != "submitBookings"
):
    st.session_state["atPage"] = "submitBookings"
    with st.spinner("Getting bookings..."):
        helpers.updateAllBookingsCache()

calendarOptions = helpers.getCalendarOptions()
calendarEvent: Dict = calendar(
    st.session_state["calendar"]["allBookingsCache"], options=calendarOptions
)
if calendarEvent.get("callback", "") == "eventClick":
    components = calendarEvent["eventClick"]["event"]["title"].split("@")
    teleHandle = components[-1][:-1]
    event = "".join(components[:-1])
    st.toast(event + f"[@{teleHandle}](https://t.me/{teleHandle}))")

isAdmin = st.session_state["userInfo"]["userType"] == "admin"
st.subheader("Submit bookings")
today = datetime.now(pytz.timezone("Singapore")).date()
startDate = st.date_input(
    "### Start date",
    value=today + timedelta(days=2),
    min_value=None if isAdmin else today,
    max_value=None if isAdmin else today + timedelta(weeks=2),
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

bookingDescription = "Regular booking"
if st.session_state["userInfo"]["userType"] == "admin":
    bookingDescription = st.text_input("Booking description", value="Regular booking")

friendList: List = st.session_state["bookingForm"]["friendIds"]
allUsers = helpers.getAllUsers()
friends = st.multiselect(
    "Booking used with:", options=allUsers, placeholder="Enter names..."
)
friendIds = [allUsers[friend] for friend in friends]

if st.button("Submit", type="primary", disabled=endTs is None or startTs is None):
    try:
        validations.verifyBookingPeriod(startTs, endTs)
        with st.spinner("Processing booking..."):
            helpers.tryInsertBooking(
                startTs,
                endTs,
                st.session_state["userInfo"]["studentId"],
                st.session_state["userInfo"]["teleHandle"],
                st.session_state["userInfo"]["name"],
                friendIds=friendIds,
                event=bookingDescription,
            )
        st.info("Booking submitted!")
    except ValueError as e:
        st.warning(str(e))
