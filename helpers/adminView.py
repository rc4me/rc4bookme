import streamlit as st
import pandas as pd
import json
from typing import List, Dict

from helpers import database


def getAdminBookings() -> List[Dict]:
    database.refreshBookings()
    df = st.session_state["db"]["bookings"]
    newdf = pd.DataFrame()
    colourMappings = {
        "A": "green",
        "P": "#8B8000",
        "R": "red",
    }
    newdf["title"] = (
        df["booking_description"] + " - " + df["name"] + " (@" + df["tele_handle"] + ")"
    )
    newdf["color"] = df["status"].replace(colourMappings)
    newdf["start"] = df["start_unix_ms"]
    newdf["end"] = df["end_unix_ms"]
    return newdf.to_dict(orient="records")


def updateAdminBookingsCache():
    st.session_state["calendar"]["adminBookingsCache"] = getAdminBookings()


def getCalendarOptions() -> Dict:
    with open("resources/allBookingsCalendarOptions.json") as file:
        options = json.load(file)
    return options
