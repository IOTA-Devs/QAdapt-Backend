import re
from datetime import date, datetime
from calendar import monthrange

monthNamesAbbr = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec"
}

def sanitize_search_query(search_query: str):
    sanitized_query = re.sub(r'[^A-Za-z0-9 ]+', '', search_query)

    return sanitized_query

def add_months(current_date: date, months: int):
    years_to_add = (current_date.month + months - 1) // 12
    curr_month = (current_date.month + months - 1) % 12 + 1
    day = current_date.day

    month_range = monthrange(current_date.year + years_to_add, curr_month)

    if month_range[1] < day:
        day -= month_range[1]

    new_date = datetime(
        current_date.year + years_to_add,
        curr_month,
        day
    )

    return new_date.date()