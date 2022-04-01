"""
Configuration of the time variables
"""
from os import getenv
from datetime import datetime, timedelta

from dateutil.tz import UTC

time_delta_m = int(getenv("TIME_PERIOD_M"))
time_delta_d = time_delta_m * 30.5
try:
    today = datetime.strptime(getenv("FIXED_TODAY_DATE"), "%Y-%m-%d").replace(
        tzinfo=UTC
    )
    print("Today = " + str(today))
except TypeError:
    print("Today date is not fixed, using datetime.today()")
    today = datetime.today().replace(tzinfo=UTC)
date_n_days_ago = today - timedelta(time_delta_d)
