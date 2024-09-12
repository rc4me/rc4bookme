import streamlit as st
import json
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import pandas as pd

from backend import database


# @st.cache_data(spinner=false)
def getCalendarOptions() -> Dict:
    with open("resources/allBookingsCalendarOptions.json") as file:
        options = json.load(file)
    return options


@st.cache_data(ttl=timedelta(minutes=5), show_spinner=False)
def getAllUsers() -> Dict[str, str]:
    df: pd.DataFrame = st.session_state["db"]["users"]
    usersDf = pd.DataFrame()
    usersDf["description"] = df["name"] + " (E***" + df["student_id"].str[4:] + ")"
    usersDf["studentId"] = df["student_id"].copy()
    return usersDf.set_index("description", drop=True)["studentId"].to_dict()


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
    studentId = st.session_state["userInfo"]["studentId"]
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
    newDf["color"] = df.apply(
        lambda row: "green"
        if row["student_id"] == studentId or studentId in row["friend_ids"]
        else "gray",
        axis=1,
    )
    return newDf.to_dict(orient="records")


def updateAllBookingsCache():
    st.session_state["calendar"]["allBookingsCache"] = getBookingsForCalendar()
