import streamlit as st
import json
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import pandas as pd

from helpers import database


# @st.cache_data(spinner=false)
def getCalendarOptions() -> Dict:
    with open("resources/allBookingsCalendarOptions.json") as file:
        options = json.load(file)
    return options


@st.cache_data(ttl=timedelta(minutes=1), show_spinner=False)
def getAllUsers() -> Dict[str, str]:
    df: pd.DataFrame = st.session_state["db"]["users"]
    usersDf = pd.DataFrame()
    usersDf["description"] = df["name"] + " (E***" + df["student_id"].str[4:] + ")"
    usersDf["studentId"] = df["student_id"].copy()
    usersDict = usersDf.set_index("description", drop=True)["studentId"].to_dict()

    userInfo = st.session_state["userInfo"]
    selfName = userInfo["name"]
    selfStudentId = userInfo["studentId"]
    del usersDict[selfName + " (E***" + selfStudentId[4:] + ")"]
    return usersDict


def tryInsertBooking(
    startTs: datetime,
    endTs: datetime,
    studentId: str,
    teleHandle: str,
    phoneNumber: str,
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
        phoneNumber,
        bookingDescription=event,
        friendIds=friendIds,
    )


def getBookingsForCalendar() -> List[Dict]:
    df = database.getPendingAndApprovedBookings()
    if len(df) == 0:
        return []

    studentId = st.session_state["userInfo"]["studentId"]
    newDf = pd.DataFrame()
    newDf["start"] = df["start_unix_ms"]
    newDf["end"] = df["end_unix_ms"]
    newDf["title"] = df.apply(
        lambda row: (
            (row["booking_description"] if row["status"] == "A" else "Pending booking")
            + " - booked by "
            + row["name"]
            + " (@"
            + row["tele_handle"]
            + ")"
        ),
        axis=1,
    )
    newDf["color"] = df.apply(
        lambda row: "green"
        if row["student_id"] == studentId or studentId in row["friend_ids"]
        else ("#2E8D87" if row["status"] == "A" else "gray"),
        axis=1,
    )
    return newDf.to_dict(orient="records")


def updateAllBookingsCache():
    st.session_state["calendar"]["allBookingsCache"] = getBookingsForCalendar()
