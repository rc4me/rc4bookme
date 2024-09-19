import streamlit as st
from typing import List


@st.cache_data()
def getRoomNumbers() -> List[str]:
    roomNumbers = [
        f"#{level:02}-{suiteNumber}{suiteUnit}"
        for level in range(3, 18)
        for suiteNumber in ["01", "11", "12"]
        for suiteUnit in ["A", "B", "C", "D", "E", "F"]
    ]
    roomNumbers += [
        f"#{level:02}-{suiteNumber:02}"
        for level in range(3, 18)
        for suiteNumber in range(2, 11)
    ]
    roomNumbers += [
        f"#{level:02}-{suiteNumber:02}"
        for level in range(3, 18)
        for suiteNumber in range(13, 28)
    ]
    return sorted(roomNumbers)
