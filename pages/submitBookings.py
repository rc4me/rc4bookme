import streamlit as st
from streamlit_calendar import calendar
from datetime import timedelta, datetime
import pytz
from typing import List, Dict

st.set_page_config("RC4ME - Book", layout="wide", page_icon="resources/rc4meLogo.png")

from utils import validations
from helpers import menu
import helpers.submitBookings as helpers

menu.redirectIfUnauthenticated()
menu.displayMenu()

# st.json(st.session_state, expanded=False)

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
custom_css = """
    .fc-daygrid-event {
        white-space: normal !important;
        overflow: hidden !important;
    }
    .fc-daygrid-event .fc-event-main {
        display: flex !important;
        flex-direction: column !important;
        padding: 2px 4px !important;
    }
    .fc-daygrid-event .fc-event-time {
        font-weight: bold !important;
        font-size: 0.85em !important;
    }
    .fc-event-title {
        white-space: normal !important;
        overflow-wrap: break-word !important;
        word-break: break-word !important;
        font-size: 0.85em !important;
    }
    .fc-daygrid-day-events {
        overflow: hidden !important;
    }
    .fc-daygrid-event-harness {
        margin-bottom: 2px !important;
    }
    .fc-list {
        max-height: 700px !important;
        overflow-y: auto !important;
    }
    .fc-timegrid-now-indicator-line {
        border-color: #FFFFFF !important;
        border-width: 2px !important;
        border-style: solid !important;
    }
    .fc-timegrid-now-indicator-arrow {
        display: none !important;
    }
"""

calendarEvent: Dict = calendar(
    st.session_state["calendar"]["allBookingsCache"], options=calendarOptions, custom_css=custom_css
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
if st.checkbox("I'm using TR3 with friends!"):
    friends = st.multiselect(
        "Booking used with:", options=allUsers, placeholder="Enter names..."
    )
else:
    friends = []
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
                st.session_state["userInfo"]["phoneNumber"],
                st.session_state["userInfo"]["name"],
                friendIds=friendIds,
                event=bookingDescription,
            )
        st.info("Booking submitted!")
    except ValueError as e:
        st.error(str(e))
