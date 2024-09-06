import streamlit as st
from typing import Dict, List
from streamlit_gsheets import GSheetsConnection
import gspread
import json
from datetime import datetime, date, time
import pandas as pd

conn = st.connection("gsheets", type=GSheetsConnection)
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

# creds = ServiceAccountCredentials.from_json_keyfile_name(
#     "resources/service_account_credentials.json", scope
# )
# client = gspread.authorize(creds)

client = gspread.service_account_from_dict(st.secrets["serviceAccount"], scopes=scope)

def isRegisteredUser(email: str) -> bool:
    isRegisteredUser = (
        conn.query(
            sql="SELECT COUNT(*) AS count FROM Users WHERE email='" + email + "'",
            ttl="10s",
        ).loc[0, "count"]
        == 1
    )
    return isRegisteredUser


def getUserDetails(email: str) -> Dict[str, str]:
    df = conn.query(
        sql="SELECT name, student_id AS studentId, "
        f"tele_handle AS teleHandle FROM Users WHERE email='{email}'",
        ttl="10s",
    )
    return dict(df.loc[0])


def isAlreadyRegistered(studentId: str, teleHandle: str):
    studentId = studentId.upper()
    teleHandle = teleHandle.strip("@")
    isAlreadyRegistered = conn.query(
        sql="SELECT COUNT(*) AS count from Users "
        f"WHERE student_id = '{studentId}'"
        f"OR tele_handle = '{teleHandle}'"
    ).loc[0, "count"] >= 1
    return isAlreadyRegistered


def registerStudent(
    studentId: str,
    teleHandle: str,
    email: str,
    name: str,
    gradYear: int,
) -> None:
    sheet = client.open("RC4MEDB").worksheet("Users")
    row = [
        email,
        name.title(),
        studentId.upper(),
        teleHandle.strip("@"),
        gradYear,
    ]
    sheet.append_row(row)


def timeSlotIsTaken(startTime: datetime, endTime: datetime) -> bool:
    startTime = startTime.timestamp() * 1000
    endTime = endTime.timestamp() * 1000
    timeSlotIsTaken = (
        conn.query(
            sql="SELECT COUNT(*) AS count FROM Bookings "
            f"WHERE start_unix_ms < {endTime} "
            f"AND end_unix_ms > {startTime}"
            "AND (status == 'A' OR status == 'a')",
            ttl="1s",
        ).loc[0, "count"]
        >= 1
    )
    return timeSlotIsTaken


def addBooking(
    name: str,
    startTs: datetime,
    endTs: datetime,
    studentId: str,
    teleHandle: str,
    bookingDescription: str,
    friendIds: List[str],
):
    sheet = client.open("RC4MEDB").worksheet("Bookings")
    row = [
        name,
        datetime.now().isoformat(),
        "P",
        startTs.date().isoformat(),
        startTs.time().isoformat(),
        endTs.date().isoformat(),
        endTs.time().isoformat(),
        studentId,
        teleHandle,
        bookingDescription,
        json.dumps(friendIds),
        startTs.timestamp() * 1000,
        endTs.timestamp() * 1000,
    ]
    sheet.append_row(row)


def getApprovedBookingsInRange(startDate: date, endDate: date) -> pd.DataFrame:
    midnight = time(0, 0, 0)
    startTs = datetime.combine(startDate, midnight)
    endTs = datetime.combine(endDate, midnight)
    return conn.query(
        sql="SELECT name, tele_handle, booking_description, start_unix_ms, end_unix_ms FROM Bookings "
        f"WHERE start_unix_ms < {endTs.timestamp() * 1000} "
        f"AND end_unix_ms > {startTs.timestamp() * 1000} "
        "AND (status = 'a' or status = 'A')",
        ttl="1s",
    )
    
def getBookingsByUser(startDate: date, endDate: date, studentId: str) -> pd.DataFrame:
    midnight = time(0, 0, 0)
    startTs = datetime.combine(startDate, midnight)
    endTs = datetime.combine(endDate, midnight)
    return conn.query(
        sql="SELECT start_unix_ms, end_unix_ms, status, booking_description FROM Bookings "
        f"WHERE start_unix_ms < {endTs.timestamp() * 1000} "
        f"AND end_unix_ms > {startTs.timestamp() * 1000} "
        f"AND student_id = '{studentId}'",
        ttl="1s",
    )
    