#######################################################################################################
#
#                       Internal statistics
#
#######################################################################################################
from datetime import datetime, timedelta
from os import getenv
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import sqlalchemy


# postgresql://admin:admin@localhost:5432/ibnse
DB_ENGINE = sqlalchemy.create_engine(getenv("DATABASE_URL"))
SQL_PATH = Path(__file__).parent.absolute() / "sql"


def get_bsd_created(bsdd_data: pd.DataFrame) -> pd.DataFrame:
    df = (
        bsdd_data.groupby(by=pd.Grouper(key="createdAt", freq="1W"))
        .count()
        .reset_index()
    )
    return df


# Sent BSDD
# @appcache.memoize(timeout=cache_timeout)
def get_recent_bsdd_sent(bsdd_data: pd.DataFrame) -> pd.DataFrame:

    now = datetime.now(tz=ZoneInfo("Europe/Paris")).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    bsdd_data = bsdd_data[
        (
            (bsdd_data["sentAt"] >= "2021-01-01")
            & (bsdd_data["sentAt"] < (now - timedelta(days=(now.toordinal() % 7) - 1)))
        )
        | bsdd_data["sentAt"].isna()
    ]
    grouped = (
        bsdd_data.groupby(by=pd.Grouper(key="sentAt", freq="1W"))["id"]
        .count()
        .reset_index()
    )

    return grouped


# Received BSDD
# @appcache.memoize(timeout=cache_timeout)
def get_recent_bsdd_received(bsdd_data: pd.DataFrame) -> pd.DataFrame:

    now = datetime.now(tz=ZoneInfo("Europe/Paris")).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    bsdd_data = bsdd_data[
        (
            (bsdd_data["receivedAt"] >= "2021-01-01")
            & (
                bsdd_data["receivedAt"]
                < (now - timedelta(days=(now.toordinal() % 7) - 1))
            )
        )
        | bsdd_data["receivedAt"].isna()
    ]
    grouped = (
        bsdd_data.groupby(by=pd.Grouper(key="receivedAt", freq="1W"))["id"]
        .count()
        .reset_index()
    )

    return grouped
