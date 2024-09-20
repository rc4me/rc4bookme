import streamlit as st
from typing import List
from utils import states


@st.cache_data()
def getRoomNumbers() -> List[str]:
    roomNumbers = [
        f"#{level:02}-{suiteNumber}{suiteUnit}"
        for level in range(3, 18)
        for suiteNumber in ["01", "11", "12"]
        for suiteUnit in ["A", "B", "C", "D", "E", "F"]
    ]
    roomNumbers += [
        f"#{level:02}-{unit:02}" for level in range(3, 18) for unit in range(2, 11)
    ]
    roomNumbers += [
        f"#{level:02}-{unit:02}" for level in range(3, 18) for unit in range(13, 28)
    ]
    return sorted(roomNumbers)


def initialiseSessionStates():
    states.setState("bookingForm", {"friendIds": []})
    states.setState(
        "db",
        {"bookings": None, "users": None},
    )
    states.setState("atPage", "main")
    states.setState(
        "calendar",
        {
            "allBookingsCache": None,
            "userBookingsCache": None,
            "adminBookingsCache": None,
        },
    )
    states.setState("notification", None)
    states.setState("userInfo", {})
    states.setState("isLoggedIn", False)
    states.setState("isRegisteredUser", None)
