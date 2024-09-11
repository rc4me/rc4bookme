import streamlit as st
import json
from typing import Dict, Tuple, Optional, List
from datetime import date, time, datetime, timedelta
import pandas as pd
import pytz

from backend import database


# @st.cache_data(spinner=false)
def getCalendarOptions() -> Dict:
    with open("resources/allBookingsCalendarOptions.json") as file:
        options = json.load(file)
    return options


def tryInsertBooking(
    startTs: datetime,
    endTs: datetime,
    studentId: str,
    teleHandle: str,
    name: str,
    event: Optional[str] = "Regular booking",
    friendIds: Optional[List[str]] = [],
):
    if database.timeSlotIsTaken(startTs, endTs):
        raise ValueError("Time slot has already been taken")
    database.addBooking(
        name,
        startTs,
        endTs,
        studentId,
        teleHandle,
        bookingDescription=event,
        friendIds=friendIds,
    )


def getBookingsForCalendar() -> List:
    df = database.getApprovedBookings()
    newDf = pd.DataFrame()
    newDf["start"] = df["start_unix_ms"]
    newDf["end"] = df["end_unix_ms"]
    newDf["title"] = (
        df["booking_description"]
        + " - booked by "
        + df["name"]
        + " (@"
        + df["tele_handle"]
        + ")"
    )
    newDf["color"] = df["student_id"].apply(
        lambda x: "green" if x == st.session_state["userInfo"]["studentId"] else "gray"
    )
    return newDf.to_dict(orient="records")


def updateAllBookingsCache():
    st.session_state["calendar"]["allBookingsCache"] = getBookingsForCalendar()
