import streamlit as st
from typing import Dict
from streamlit_calendar import calendar
from datetime import datetime

st.set_page_config(
    "RC4ME - Admin View", layout="wide", page_icon="resources/rc4meLogo.png"
)

from helpers import menu, database
from helpers import notifications
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
"""

calendarEvent: Dict = calendar(
    st.session_state["calendar"]["adminBookingsCache"], options=calendarOptions, custom_css=custom_css
)

if calendarEvent.get("callback", "") == "eventClick":
    event = calendarEvent["eventClick"]["event"]
    bookingUid = event["extendedProps"]["uuid"]
    booking = database.getBookingByUid(bookingUid)
    booking["start"] = (
        booking["booking_start_date"] + " " + booking["booking_start_time"]
    )
    booking["end"] = booking["booking_end_date"] + " " + booking["booking_end_time"]
    start = datetime.fromisoformat(event["start"])
    end = datetime.fromisoformat(event["end"])

    st.subheader(event["title"])
    st.dataframe(
        booking[
            [
                "start",
                "end",
                "name",
                "student_id",
                "phone_number",
                "friend_ids",
                "tele_handle",
                "booking_description",
                "status",
            ]
        ],
        use_container_width=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    adminName = st.session_state["userInfo"].get("name", "Unknown Admin")
    try:
        with col1:
            if st.button(
                "Mark as approved", type="primary", disabled=booking["status"] == "A"
            ):
                with st.spinner("Approving booking..."):
                    database.editBookingStatus(bookingUid, "A")
                    helpers.updateAdminBookingsCache()
                try:
                    notifications.notifyAdminAction(
                        "approved", adminName, booking["booking_description"],
                        booking["name"], booking["student_id"], start, end,
                        booking["booking_description"],
                    )
                    st.session_state["notification"] = f"Booking by {booking['name']} on {start.strftime('%c')} approved!"
                except Exception as e:
                    st.session_state["notification"] = f"Booking by {booking['name']} on {start.strftime('%c')} approved!"
                st.rerun()
        with col2:
            if st.button("Mark as pending", disabled=booking["status"] == "P"):
                with st.spinner("Marking booking as pending..."):
                    database.editBookingStatus(bookingUid, "P")
                    helpers.updateAdminBookingsCache()
                try:
                    notifications.notifyAdminAction(
                        "pending", adminName, booking["booking_description"],
                        booking["name"], booking["student_id"], start, end,
                        booking["booking_description"],
                    )
                    st.session_state["notification"] = f"Booking by {booking['name']} on {start.strftime('%c')} marked as pending."
                except Exception as e:
                    st.session_state["notification"] = f"Booking by {booking['name']} on {start.strftime('%c')} marked as pending."
                st.rerun()
        with col3:
            if st.button("Mark as rejected", disabled=booking["status"] == "R"):
                with st.spinner("Rejecting booking..."):
                    database.editBookingStatus(bookingUid, "R")
                    helpers.updateAdminBookingsCache()
                try:
                    notifications.notifyAdminAction(
                        "rejected", adminName, booking["booking_description"],
                        booking["name"], booking["student_id"], start, end,
                        booking["booking_description"],
                    )
                    st.session_state["notification"] = f"Booking by {booking['name']} on {start.strftime('%c')} rejected."
                except Exception as e:
                    st.session_state["notification"] = f"Booking by {booking['name']} on {start.strftime('%c')} rejected."
                st.rerun()
        with col4:
            if st.button("Delete booking"):
                with st.spinner("Deleting booking..."):
                    database.deleteBooking(bookingUid)
                    helpers.updateAdminBookingsCache()
                try:
                    notifications.notifyAdminAction(
                        "deleted", adminName, booking["booking_description"],
                        booking["name"], booking["student_id"], start, end,
                        booking["booking_description"],
                    )
                    st.session_state["notification"] = f"Booking by {booking['name']} on {start.strftime('%c')} deleted."
                except Exception as e:
                    st.session_state["notification"] = f"Booking by {booking['name']} on {start.strftime('%c')} deleted."
                st.rerun()
    except KeyError as e:
        st.error(str(e))
else:
    st.markdown("Click on any booking to view actions.")
