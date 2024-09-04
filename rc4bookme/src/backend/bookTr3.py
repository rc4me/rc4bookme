import streamlit as st
import json
from typing import Dict, Tuple
from datetime import date, time, datetime, timedelta


def getValidDateRange():
    return [date.today() - timedelta(weeks=4), date.today() + timedelta(weeks=6)]


# @st.cache_data(ttl=timedelta(days=1))
def getCalendarOptions() -> Dict:
    dateRange = getValidDateRange()
    with open("resources/calendarOptions.json") as file:
        options = json.load(file)
    options["validRange"] = {
        "start": str(dateRange[0]),
        "end": str(dateRange[1]),
    }
    return options


def getDatetime(
    startDate: date, endDate: date, startTime: time, endTime: time
) -> Tuple[datetime, datetime]:
    start = datetime.combine(startDate, startTime)
    end = datetime.combine(endDate, endTime)
    if start > end:
        raise ValueError("End time cannot be earlier than start time")
    else:
        return start, end
