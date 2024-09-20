import streamlit as st
from streamlit_calendar import calendar
import pytz
from datetime import timedelta, datetime

st.set_page_config(
    "RC4ME - View Bookings", layout="wide", page_icon="resources/rc4meLogo.png"
)

import helpers.viewYourBookings as helpers
from helpers import menu, database
from utils import validations

menu.redirectIfUnauthenticated()
menu.displayMenu()

calendarsState = st.session_state["calendar"]
studentId = st.session_state["userInfo"]["studentId"]

st.title("View bookings")
# st.json(st.session_state, expanded=False)
if (
    st.session_state["calendar"]["userBookingsCache"] is None
    or st.button("Refresh calendar")
    or st.session_state["atPage"] != "viewYourBookings"
):
    st.session_state["notification"] = None
    st.session_state["atPage"] = "viewYourBookings"
    with st.spinner("Getting bookings..."):
        helpers.updateUserBookingsCache(studentId)

if st.session_state["notification"] is not None:
    st.info(st.session_state["notification"])

calendarOptions = helpers.getCalendarOptions()
calendarEvent = calendar(
    st.session_state["calendar"]["userBookingsCache"], options=calendarOptions
)


pendingEventClicked = False
if calendarEvent.get("callback", "") == "eventClick":
    bookingUid = calendarEvent["eventClick"]["event"]["extendedProps"]["uuid"]
    try:
        booking = database.getBookingByUid(bookingUid)
    except KeyError:
        booking = {"status": ""}
    if booking["status"] == "P":
        pendingEventClicked = True
        isAdmin = st.session_state["userInfo"]["userType"] == "admin"
        oldStartTs = datetime.fromtimestamp(
            booking["start_unix_ms"] / 1000, tz=pytz.timezone("Singapore")
        )
        oldEndTs = datetime.fromtimestamp(
            booking["end_unix_ms"] / 1000, tz=pytz.timezone("Singapore")
        )

        st.subheader(f"Edit / cancel booking on {oldStartTs.strftime("%c")}")
        oldDuration = oldEndTs - oldStartTs
        today = datetime.now(pytz.timezone("Singapore")).date()

        newStartDate = st.date_input(
            "### Start date",
            value=oldStartTs.date(),
            min_value=None if isAdmin else today,
            max_value=None if isAdmin else today + timedelta(weeks=2),
        )
        newStartTime = st.time_input(
            "### Start time", step=timedelta(hours=0.5), value=oldStartTs.time()
        )
        newStartTs = pytz.timezone("Singapore").localize(
            datetime.combine(newStartDate, newStartTime)
        )

        defaultEndTs = newStartTs + oldDuration
        newEndDate = st.date_input(
            "### End date",
            min_value=newStartDate,
            value=defaultEndTs.date(),
        )
        newEndTime = st.time_input(
            "### End time",
            step=timedelta(hours=0.5),
            value=defaultEndTs.time(),
        )
        newEndTs = pytz.timezone("Singapore").localize(
            datetime.combine(newEndDate, newEndTime)
        )

        hasEditedBooking = newEndTs != oldEndTs or newStartTs != oldStartTs
        if st.button("Edit booking", type="primary", disabled=not hasEditedBooking):
            try:
                with st.spinner("Editing booking..."):
                    validations.verifyBookingPeriod(newStartTs, newEndTs)
                    if database.timeSlotIsTaken(newStartTs, newEndTs):
                        raise ValueError("Time slot has already been taken")
                    database.editBookingTiming(bookingUid, newStartTs, newEndTs)
                    helpers.updateUserBookingsCache(studentId)
                st.session_state["notification"] = (
                    f"Booking on {oldStartTs.date().isoformat()} edited!"
                )
                st.rerun()
            except (ValueError, KeyError) as e:
                st.error(str(e))
        if st.button("Cancel booking", type="primary"):
            try:
                with st.spinner("Cancelling booking..."):
                    database.deleteBooking(bookingUid)
                    helpers.updateUserBookingsCache(studentId)
                st.session_state["notification"] = (
                    f"Booking on {oldStartTs.date().isoformat()} cancelled."
                )
                st.rerun()
            except KeyError as e:
                st.error(str(e))

if not pendingEventClicked:
    st.markdown("Click on any pending bookings to edit or cancel them.")
