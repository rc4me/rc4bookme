import streamlit as st
import json
from typing import Dict, Tuple, Optional, List
from datetime import date, time, datetime, timedelta
import pandas as pd

from backend import database


def getValidDateRange() -> Tuple[date, date]:
    return date.today() - timedelta(weeks=4), date.today() + timedelta(weeks=6)


# @st.cache_data(ttl=timedelta(days=1))
def getCalendarOptions() -> Dict:
    startDate, endDate = getValidDateRange()
    with open("resources/allBookingsCalendarOptions.json") as file:
        options = json.load(file)
    options["validRange"] = {
        "start": str(startDate),
        "end": str(endDate),
    }
    return options


def getBookingTs(
    startDate: date, endDate: date, startTime: time, endTime: time
) -> Tuple[datetime, datetime]:
    start = datetime.combine(startDate, startTime)
    end = datetime.combine(endDate, endTime)
    if start > end:
        raise ValueError("End time cannot be earlier than start time")
    if start < datetime.now() - timedelta(hours=1):
        raise ValueError("Booking is before current time")
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
    dateRange = getValidDateRange()
    df = database.getApprovedBookingsInRange(dateRange[0], dateRange[1])
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
    return newDf.to_dict(orient="records")


def updateAllBookingsCache():
    st.session_state["calendar"]["allBookingsCache"] = getBookingsForCalendar()
