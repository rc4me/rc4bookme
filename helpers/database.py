import streamlit as st
from typing import Dict, List
import gspread
import json
from datetime import datetime
import pandas as pd
from uuid import uuid4

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
    bookingsDf = bookingsDf.set_index("booking_uid", drop=True)
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
            ["tele_handle", "student_id", "name", "phone_number", "user_type"]
        ]
        .rename(
            columns={
                "tele_handle": "teleHandle",
                "student_id": "studentId",
                "user_type": "userType",
                "phone_number": "phoneNumber",
            }
        )
        .loc[email]
    )


def isAlreadyRegistered(studentId: str, teleHandle: str, phoneNumber: str) -> bool:
    refreshUsers()
    studentId = studentId.upper()
    teleHandle = teleHandle.strip("@")
    phoneNumber = phoneNumber.replace(" ", "")
    isAlreadyRegistered = (
        studentId in st.session_state["db"]["users"]["student_id"].values
        or teleHandle in st.session_state["db"]["users"]["tele_handle"].values
        or phoneNumber in st.session_state["db"]["users"]["phone_number"].values
    )
    return isAlreadyRegistered


def registerStudent(
    studentId: str,
    teleHandle: str,
    phoneNumber: str,
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
        phoneNumber.replace(" ", ""),
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
    phoneNumber: str,
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
        str(phoneNumber),
        bookingDescription,
        json.dumps(friendIds),
        startTs.timestamp() * 1000,
        endTs.timestamp() * 1000,
        str(uuid4()),
    ]
    sheet.append_row(row)


def getPendingAndApprovedBookings() -> pd.DataFrame:
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
    ].query("(status == 'P' | status == 'A')")


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


def writeToDb(newDf: pd.DataFrame, worksheetName: str):
    """
    Overwrites the entire sheet! Use with caution.
    """
    bookingsWorksheet = spreadsheet.worksheet(worksheetName)
    bookingsWorksheet.update([newDf.columns.values.tolist()] + newDf.values.tolist())


def getBookingByUid(uuid: str) -> pd.Series:
    bookingsDf: pd.DataFrame = st.session_state["db"]["bookings"]
    booking = bookingsDf.loc[uuid,]
    return booking


def editBookingTiming(uuid: str, newStart: datetime, newEnd: datetime):
    refreshBookings()
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
        writeToDb(bookingsDf, "Bookings")
    except KeyError:
        raise KeyError("Booking not found. Please refresh your calendar")


def deleteBooking(uuid: str):
    refreshBookings()
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
        writeToDb(bookingsDf, "Bookings")
    except KeyError:
        raise KeyError("Booking not found. Please refresh your calendar")


def editBookingStatus(uuid: str, status: str):
    refreshBookings()
    bookingsDf: pd.DataFrame = st.session_state["db"]["bookings"].copy()
    try:
        bookingsDf.loc[uuid, "status"] = status
        bookingsDf["friend_ids"] = (
            bookingsDf["friend_ids"].apply(list).apply(json.dumps)
        )
        bookingsDf["booking_uid"] = bookingsDf.index
        bookingsDf = bookingsDf.reset_index(drop=True)
        writeToDb(bookingsDf, "Bookings")
    except KeyError:
        raise KeyError("Booking not found. Please refresh your calendar")
