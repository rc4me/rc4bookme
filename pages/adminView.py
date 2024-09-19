import streamlit as st
from typing import Dict
from streamlit_calendar import calendar

st.set_page_config("RC4ME - Admin View", layout="wide", page_icon="resources/rc4meLogo.png")

from helpers import menu
import helpers.adminView as helpers

menu.redirectIfNotAdmin()
menu.displayMenu()

if (
    st.button("Refresh calendar")
    or st.session_state["calendar"]["adminBookingsCache"] is None
    or st.session_state["atPage"] != "adminView"
):
    st.session_state["atPage"] = "adminView"
    with st.spinner("Getting bookings..."):
        helpers.updateAdminBookingsCache()

calendarOptions = helpers.getCalendarOptions()
calendarEvent: Dict = calendar(
    st.session_state["calendar"]["adminBookingsCache"], options=calendarOptions
)
if calendarEvent.get("callback", "") == "eventClick":
    components = calendarEvent["eventClick"]["event"]["title"].split("@")
    teleHandle = components[-1][:-1]
    event = "".join(components[:-1])
    st.toast(event + f"[@{teleHandle}](https://t.me/{teleHandle}))")