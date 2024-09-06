# import streamlit as st
# from typing import Dict
# from streamlit_gsheets import GSheetsConnection


def isValidStudentId(studentId: str | None) -> bool:
    if studentId is None or studentId == "":
        return False
    if studentId[0].lower() != "e":
        return False
    if len(studentId) != 8:
        return False
    if not studentId[1:].isnumeric():
        return False
    return True
