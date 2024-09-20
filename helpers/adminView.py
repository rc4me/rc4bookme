import streamlit as st
import pandas as pd
import json
from typing import List, Dict

from helpers import database


def getAdminBookings() -> List[Dict]:
    database.refreshBookings()
    df: pd.DataFrame = st.session_state["db"]["bookings"]
    newDf = pd.DataFrame()
    colourMappings = {
        "A": "green",
        "P": "#8B8000",
        "R": "red",
    }
    newDf["title"] = (
        df["booking_description"] + " - " + df["name"] + " (@" + df["tele_handle"] + ")"
    )
    newDf["color"] = df["status"].replace(colourMappings)
    newDf["start"] = df["start_unix_ms"]
    newDf["end"] = df["end_unix_ms"]
    newDf["extendedProps"] = df.apply(
        lambda row: {"uuid": row.name},
        axis=1,
    )
    return newDf.to_dict(orient="records")


def updateAdminBookingsCache():
    st.session_state["calendar"]["adminBookingsCache"] = getAdminBookings()


def getCalendarOptions() -> Dict:
    with open("resources/allBookingsCalendarOptions.json") as file:
        options = json.load(file)
    return options
