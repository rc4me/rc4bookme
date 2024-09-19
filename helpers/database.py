import streamlit as st
from typing import Dict, List
import gspread
import json
from datetime import datetime
import pandas as pd

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
spreadsheet = gspread.service_account_from_dict(
    st.secrets["serviceAccount"], scopes=scope
).open("RC4MEDB")


def refreshUsers():
    st.session_state["db"]["users"] = pd.DataFrame(
        spreadsheet.worksheet("Users").get_all_records()
    ).set_index("email")


def refreshBookings():
    bookingsDf = pd.DataFrame(spreadsheet.worksheet("Bookings").get_all_records())
    if len(bookingsDf) != 0:
        bookingsDf["friend_ids"] = bookingsDf["friend_ids"].apply(json.loads).apply(set)
    st.session_state["db"]["bookings"] = bookingsDf


def isRegisteredUser(email: str) -> bool:
    refreshUsers()
    isRegisteredUser = email in st.session_state["db"]["users"].index.values
    return isRegisteredUser


def getUserDetails(email: str) -> Dict[str, str]:
    refreshUsers()
    return dict(
        st.session_state["db"]["users"][
            ["tele_handle", "student_id", "name", "user_type"]
        ]
        .rename(
            columns={
                "tele_handle": "teleHandle",
                "student_id": "studentId",
                "user_type": "userType",
            }
        )
        .loc[email]
    )


def isAlreadyRegistered(studentId: str, teleHandle: str):
    refreshUsers()
    studentId = studentId.upper()
    teleHandle = teleHandle.strip("@")
    isAlreadyRegistered = (
        studentId in st.session_state["db"]["users"]["student_id"].values
        or teleHandle in st.session_state["db"]["users"]["tele_handle"].values
    )
    return isAlreadyRegistered


def registerStudent(
    studentId: str,
    teleHandle: str,
    email: str,
    name: str,
    roomNumber: str,
    gradYear: int,
) -> None:
    sheet = spreadsheet.worksheet("Users")
    row = [
        email,
        name.title(),
        studentId.upper(),
        teleHandle.strip("@"),
        roomNumber,
        gradYear,
        "user",
    ]
    sheet.append_row(row)


def timeSlotIsTaken(startTime: datetime, endTime: datetime) -> bool:
    refreshBookings()
    if len(st.session_state["db"]["bookings"]) == 0:
        return False
    startTime = startTime.timestamp() * 1000
    endTime = endTime.timestamp() * 1000
    timeSlotIsTaken = (
        len(
            st.session_state["db"]["bookings"].query(
                f"start_unix_ms < {endTime} & end_unix_ms > {startTime} & (status == 'A' | status == 'a')",
            )
        )
        > 0
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
    sheet = spreadsheet.worksheet("Bookings")
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


def getApprovedBookings() -> pd.DataFrame:
    refreshBookings()
    if len(st.session_state["db"]["bookings"]) == 0:
        return pd.DataFrame(
            columns=[
                "student_id",
                "name",
                "status",
                "tele_handle",
                "booking_description",
                "start_unix_ms",
                "end_unix_ms",
                "friend_ids",
            ]
        )
    return st.session_state["db"]["bookings"][
        [
            "student_id",
            "name",
            "status",
            "tele_handle",
            "booking_description",
            "start_unix_ms",
            "end_unix_ms",
            "friend_ids",
        ]
    ].query("(status == 'a' | status == 'A')")


def getBookingsForUser(studentId: str) -> pd.DataFrame:
    refreshBookings()
    bookingsDf: pd.DataFrame = st.session_state["db"]["bookings"]
    isRelevantToUser = bookingsDf.apply(
        lambda row: row["student_id"] == studentId
        or (studentId in row["friend_ids"] and row["status"] == "A"),
        axis=1,
    )
    if isRelevantToUser.sum() == 0:
        return pd.DataFrame(
            columns=[
                "name",
                "student_id",
                "start_unix_ms",
                "end_unix_ms",
                "status",
                "booking_description",
            ]
        )
    return bookingsDf[isRelevantToUser][
        [
            "name",
            "student_id",
            "start_unix_ms",
            "end_unix_ms",
            "status",
            "booking_description",
        ]
    ]