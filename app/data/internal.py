from datetime import datetime, timedelta
from os import getenv
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import sqlalchemy

DB_ENGINE = sqlalchemy.create_engine(getenv("DATABASE_URL"))
SQL_PATH = Path(__file__).parent.absolute() / "sql"


def get_bsd_created(bsdd_data: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a DataFrame with number of BSD(D) created by week.
    It includes non dangerous BSD also.

    Parameters
    ----------
    bsdd_data: DataFrame
        DataFrame containing BSD(D) data.
    """

    df = (
        bsdd_data.groupby(by=pd.Grouper(key="created_at", freq="1W"))
        .count()
        .reset_index()
    )
    return df


def get_recent_bsdd_sent(bsdd_data: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a DataFrame with number of BSD(D) sent by week.
    It includes non dangerous BSD also.

    Parameters
    ----------
    bsdd_data: DataFrame
        DataFrame containing BSD(D) data.
    """

    now = datetime.now(tz=ZoneInfo("Europe/Paris")).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    bsdd_data = bsdd_data[
        (
            (bsdd_data["sent_at"] >= "2022-01-01")
            & (bsdd_data["sent_at"] < (now - timedelta(days=(now.toordinal() % 7) - 1)))
        )
        | bsdd_data["sent_at"].isna()
    ]
    grouped = (
        bsdd_data.groupby(by=pd.Grouper(key="sent_at", freq="1W"))["id"]
        .count()
        .reset_index()
    )

    return grouped


def get_recent_bsdd_received(bsdd_data: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a DataFrame with number of BSD(D) received by week.
    It includes non dangerous BSD also.

    Parameters
    ----------
    bsdd_data: DataFrame
        DataFrame containing BSD(D) data.
    """

    now = datetime.now(tz=ZoneInfo("Europe/Paris")).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    bsdd_data = bsdd_data[
        (
            (bsdd_data["received_at"] >= "2022-01-01")
            & (
                bsdd_data["received_at"]
                < (now - timedelta(days=(now.toordinal() % 7) - 1))
            )
        )
        | bsdd_data["received_at"].isna()
    ]
    grouped = (
        bsdd_data.groupby(by=pd.Grouper(key="received_at", freq="1W"))["id"]
        .count()
        .reset_index()
    )

    return grouped
