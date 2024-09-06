from datetime import date, timedelta
from typing import Tuple, List, Dict
import pandas as pd
import streamlit as st
import json

from backend import database


def getDefaultDateRange() -> Tuple[date, date]:
    return date.today() - timedelta(days=2), date.today() + timedelta(weeks=4)


def getUserBookingsForCalendar(
    startDate: date, endDate: date, studentId: str
) -> List[Dict]:
    df = database.getBookingsByUser(startDate, endDate, studentId)

    mappings = {"A": "Approved", "P": "Pending", "a": "Approved", "p": "Pending", "R": "Rejected", "r": "Rejected"}
    newDf = pd.DataFrame()
    newDf["start"] = df["start_unix_ms"]
    newDf["end"] = df["end_unix_ms"]
    newDf["title"] = (
        df["booking_description"]
        + " (Status: "
        + df["status"].replace(mappings)
        + ")"
    )
    return newDf.to_dict(orient="records")


def updateUserBookingsCache(studentId: str, startTs: date, endTs: date):
    st.session_state["calendar"]["userBookingsCache"] = getUserBookingsForCalendar(
        startTs, endTs, studentId
    )


# @st.cache_data(ttl=timedelta(days=1))
def getCalendarOptions() -> Dict:
    startDate, endDate = getDefaultDateRange()
    with open("resources/userBookingsCalendarOptions.json") as file:
        options = json.load(file)
    options["validRange"] = {
        "start": str(startDate),
        "end": str(endDate),
    }
    return options
