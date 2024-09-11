from typing import List, Dict
import pandas as pd
import streamlit as st
import json

from backend import database


def getUserBookingsForCalendar(studentId: str) -> List[Dict]:
    df = database.getBookingsByUser(studentId)

    statusMappings = {
        "A": "Approved",
        "P": "Pending",
        "a": "Approved",
        "p": "Pending",
        "R": "Rejected",
        "r": "Rejected",
    }
    colourMappings = {
        "A": "green",
        "P": "yellow",
        "a": "green",
        "p": "yellow",
        "R": "red",
        "r": "red"
    }
    newDf = pd.DataFrame()
    newDf["start"] = df["start_unix_ms"] - 28800000
    newDf["end"] = df["end_unix_ms"] - 28800000
    newDf["title"] = (
        df["booking_description"] + " (Status: " + df["status"].replace(statusMappings) + ")"
    )
    newDf["color"] = df["status"].replace(colourMappings)
    return newDf.to_dict(orient="records")


def updateUserBookingsCache(studentId: str):
    st.session_state["calendar"]["userBookingsCache"] = getUserBookingsForCalendar(
        studentId
    )


# @st.cache_data(show_spinner = false)
def getCalendarOptions() -> Dict:
    with open("resources/userBookingsCalendarOptions.json") as file:
        options = json.load(file)
    return options
