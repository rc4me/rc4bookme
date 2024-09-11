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


def getBookingTs(
    startDate: date, endDate: date, startTime: time, endTime: time
) -> Tuple[datetime, datetime]:
    start = pytz.timezone("Singapore").localize(datetime.combine(startDate, startTime))
    end = pytz.timezone("Singapore").localize(datetime.combine(endDate, endTime))
    if start > end:
        raise ValueError("End time cannot be earlier than start time")
    if start - datetime.now(tz=pytz.timezone("Singapore")) < timedelta(hours=12):
        raise ValueError("Please book at least 12 hours in advance")
    if end - start < timedelta(hours=1):
        raise ValueError("Booking must be at least an hour long")
    if end - start > timedelta(hours=4):
        raise ValueError("Booking must be less than 4 hours long")
    return start, end


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
