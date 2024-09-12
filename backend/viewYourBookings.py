from typing import List, Dict
import pandas as pd
import streamlit as st
import json

from backend import database


def getUserBookingsForCalendar(studentId: str) -> List[Dict]:
    df = database.getBookingsForUser(studentId)

    statusMappings = {
        "A": "Approved",
        "P": "Pending",
        "R": "Rejected",
    }
    colourMappings = {
        "A": "green",
        "P": "yellow",
        "R": "red",
    }
    newDf = pd.DataFrame()
    newDf["start"] = df["start_unix_ms"]
    newDf["end"] = df["end_unix_ms"]
    newDf["title"] = df.apply(
        lambda row: (
            row["booking_description"]
            + " (Status: "
            + statusMappings[row["status"]]
            + ")"
        )
        if row["student_id"] == studentId
        else (row["booking_description"] + " (Booked by " + row["name"] + ")"),
        axis=1,
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
