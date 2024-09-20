import streamlit as st
from typing import Dict
from streamlit_calendar import calendar
from datetime import datetime

st.set_page_config(
    "RC4ME - Admin View", layout="wide", page_icon="resources/rc4meLogo.png"
)

from helpers import menu, database
import helpers.adminView as helpers

menu.redirectIfNotAdmin()
menu.displayMenu()


st.title("Admin view - all bookings")
if (
    st.button("Refresh calendar")
    or st.session_state["calendar"]["adminBookingsCache"] is None
    or st.session_state["atPage"] != "adminView"
):
    st.session_state["atPage"] = "adminView"
    st.session_state["notification"] = None
    with st.spinner("Getting bookings..."):
        helpers.updateAdminBookingsCache()

if st.session_state["notification"] is not None:
    st.info(st.session_state["notification"])

calendarOptions = helpers.getCalendarOptions()
calendarEvent: Dict = calendar(
    st.session_state["calendar"]["adminBookingsCache"], options=calendarOptions
)

if calendarEvent.get("callback", "") == "eventClick":
    event = calendarEvent["eventClick"]["event"]
    bookingUid = event["extendedProps"]["uuid"]
    booking = database.getBookingByUid(bookingUid)

    st.subheader(event["title"])
    st.dataframe(
        booking[
            [
                "booking_description",
                "name",
                "student_id",
                "tele_handle",
                "friend_ids",
                "status",
            ]
        ]
    )
    start = datetime.fromisoformat(event["start"])

    col1, col2, col3, col4 = st.columns(4)
    try:
        with col1:
            if st.button(
                "Mark as approved", type="primary", disabled=booking["status"] == "A"
            ):
                with st.spinner("Approving booking..."):
                    database.editBookingStatus(bookingUid, "A")
                    helpers.updateAdminBookingsCache()
                st.session_state["notification"] = (
                    f"Booking by {booking['name']} on {start.strftime('%c')} approved!"
                )
                st.rerun()
        with col2:
            if st.button("Mark as pending", disabled=booking["status"] == "P"):
                with st.spinner("Marking booking as pending..."):
                    database.editBookingStatus(bookingUid, "P")
                    helpers.updateAdminBookingsCache()
                st.session_state["notification"] = (
                    f"Booking by {booking['name']} on {start.strftime('%c')} marked as pending."
                )
                st.rerun()
        with col3:
            if st.button("Mark as rejected", disabled=booking["status"] == "R"):
                with st.spinner("Rejecting booking..."):
                    database.editBookingStatus(bookingUid, "R")
                    helpers.updateAdminBookingsCache()
                st.session_state["notification"] = (
                    f"Booking by {booking['name']} on {start.strftime('%c')} rejected."
                )
                st.rerun()
        with col4:
            if st.button("Delete booking"):
                with st.spinner("Deleting booking..."):
                    database.deleteBooking(bookingUid)
                    helpers.updateAdminBookingsCache()
                st.session_state["notification"] = (
                    f"Booking by {booking['name']} on {start.strftime('%c')} deleted."
                )
                st.rerun()
    except KeyError as e:
        st.error(str(e))
else:
    st.markdown("Click on any booking to view actions.")