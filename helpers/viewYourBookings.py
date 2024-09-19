from typing import List, Dict
import pandas as pd
import streamlit as st
import json
from datetime import datetime

from helpers import database


def getUserBookingsForCalendar(studentId: str) -> List[Dict]:
    df = database.getBookingsForUser(studentId)
    if len(df) == 0:
        return []

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
    newDf["extendedProps"] = df.apply(lambda row: {"uuid": row.name}, axis=1)
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


def getBookingByUid(uuid: str) -> pd.Series:
    bookingsDf: pd.DataFrame = st.session_state["db"]["bookings"]
    booking = bookingsDf.loc[uuid,]
    return booking


def editBookingTiming(uuid: str, newStart: datetime, newEnd: datetime):
    database.refreshBookings()
    bookingsDf: pd.DataFrame = st.session_state["db"]["bookings"].copy()
    try:
        bookingsDf.loc[
            uuid,
            [
                "booking_start_date",
                "booking_start_time",
                "booking_end_date",
                "booking_end_time",
                "start_unix_ms",
                "end_unix_ms",
            ],
        ] = (
            newStart.date().isoformat(),
            newStart.time().isoformat(),
            newEnd.date().isoformat(),
            newEnd.time().isoformat(),
            newStart.timestamp() * 1000,
            newEnd.timestamp() * 1000,
        )
        bookingsDf["friend_ids"] = (
            bookingsDf["friend_ids"].apply(list).apply(json.dumps)
        )
        bookingsDf["booking_uid"] = bookingsDf.index
        bookingsDf = bookingsDf.reset_index(drop=True)
        database.writeToDb(bookingsDf, "Bookings")
    except KeyError:
        raise KeyError("Booking not found. Please refresh your calendar")


def cancelBooking(uuid: str):
    database.refreshBookings()
    bookingsDf: pd.DataFrame = st.session_state["db"]["bookings"].copy()
    try:
        bookingsDf = bookingsDf.drop(index=uuid)
        bookingsDf["friend_ids"] = (
            bookingsDf["friend_ids"].apply(list).apply(json.dumps)
        )
        bookingsDf["booking_uid"] = bookingsDf.index
        bookingsDf = bookingsDf.reset_index(drop=True)
        dummyRow = pd.DataFrame(
            [["" for column in bookingsDf.columns]], columns=bookingsDf.columns
        )
        bookingsDf = pd.concat([bookingsDf, dummyRow])
        database.writeToDb(bookingsDf, "Bookings")
    except KeyError:
        raise KeyError("Booking not found. Please refresh your calendar")
