from datetime import datetime, time, timedelta, timezone


def get_current_day() -> tuple[datetime, datetime]:
    now = datetime.now()
    today = now.date()

    start = datetime.combine(today, time.min)
    end = datetime.combine(today, time.max)

    return start, end


def get_current_week() -> tuple[datetime, datetime]:
    now = datetime.now()
    today = now.date()

    start_date = today - timedelta(days=today.weekday())
    start = datetime.combine(start_date, time.min)

    end = start + timedelta(days=7)

    return start, end


def get_current_month() -> tuple[datetime, datetime]:
    now = datetime.now()
    today = now.date()

    start = datetime.combine(today.replace(day=1), time.min)

    if today.month == 12:
        next_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month + 1, day=1)

    end = datetime.combine(next_month, time.min)

    return start, end


def get_current_year() -> tuple[datetime, datetime]:
    now = datetime.now()

    start = datetime(year=now.year, month=1, day=1)

    end = datetime(year=now.year + 1, month=1, day=1)

    return start, end
