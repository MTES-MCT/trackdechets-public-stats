"""
Configuration of the time variables
"""
from os import getenv
from datetime import datetime, timedelta

from dateutil.tz import UTC

time_delta_m = int(getenv("TIME_PERIOD_M"))
time_delta_d = time_delta_m * 30.5


def get_today_datetime():
    try:
        today = datetime.strptime(getenv("FIXED_TODAY_DATE"), "%Y-%m-%d").replace(
            tzinfo=UTC
        )
        print("Today = " + str(today))
    except TypeError:
        today = datetime.today().replace(tzinfo=UTC)

    return today


def get_today_n_days_ago(today):
    return today - timedelta(time_delta_d)
