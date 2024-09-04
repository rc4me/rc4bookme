import streamlit as st
from typing import Dict
from streamlit_gsheets import GSheetsConnection
import gspread
from oauth2client.service_account import ServiceAccountCredentials


conn = st.connection("gsheets", type=GSheetsConnection)


def isRegisteredUser(email: str) -> bool:
    isRegisteredUser = (
        conn.query(
            sql="SELECT COUNT(*) AS count FROM Users WHERE email='" + email + "'",
            ttl="10s",
        ).loc[0, "count"]
        == 1
    )
    return isRegisteredUser


def getStudentId(email: str) -> str:
    return conn.query(
        sql="SELECT student_id FROM Users WHERE email='" + email + "'",
        ttl="10s",
    ).loc[0, "student_id"]


def registerStudent(
    studentId: str,
    teleHandle: str,
    userInfo: Dict,
    gradYear: int,
) -> None:
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "resources/service_account_credentials.json", scope
    )
    client = gspread.authorize(creds)

    sheet = client.open("RC4MEDB").worksheet("Users")
    row = [
        userInfo["email"],
        userInfo["name"],
        studentId.upper(),
        teleHandle.strip("@"),
        gradYear,
    ]
    sheet.append_row(row)
    
