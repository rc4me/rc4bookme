from datetime import datetime, timedelta
import pytz


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


def verifyBookingPeriod(start: datetime, end: datetime):
    if start > end:
        raise ValueError("End time cannot be earlier than start time")
    if start - datetime.now(tz=pytz.timezone("Singapore")) < timedelta(hours=12):
        raise ValueError("Please book at least 12 hours in advance")
    if end - start < timedelta(hours=1):
        raise ValueError("Booking must be at least an hour long")
    if end - start > timedelta(hours=4):
        raise ValueError("Booking must be less than 4 hours long")
