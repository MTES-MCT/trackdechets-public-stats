"""
Data gathering and processing
"""
import time
from datetime import datetime, timedelta
from os import getenv
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import sqlalchemy

DB_ENGINE = sqlalchemy.create_engine(getenv("DATABASE_URL"))
SQL_PATH = Path(__file__).parent.absolute() / "sql"


def get_bs_data(
    sql_path: Path,
    include_drafts: bool = False,
    include_only_dangerous_waste: bool = True,
) -> pd.DataFrame:
    """
    Queries the configured database for BSx data. The query should select the columns needed to
    create the figures of the application.

    Parameters
    ----------
    sql_path: PathLike
        Path of the sql query file. Query must select at least a "createdAt" column.
    include_drafts: bool
        Wether to include drafts BSx in the result.

    Returns
    -------
    DataFrame
        dataframe of BSx, with all data included in the sql query.
    """

    started_time = time.time()

    sql_query = sql_path.read_text()
    bs_data_df = pd.read_sql_query(
        sql_query,
        con=DB_ENGINE,
    )

    for col_name in ["createdAt", "sentAt", "receivedAt", "processedAt"]:
        bs_data_df[col_name] = pd.to_datetime(
            bs_data_df[col_name], utc=True, errors="coerce"
        ).dt.tz_convert("Europe/Paris")

    now = datetime.now(tz=ZoneInfo("Europe/Paris")).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    # This is to handle specific case when sqlalchemy does not handle well the timezone
    # and there is data at midnight Paris time the last day of the time window we want to keep
    # that is return by the query but shouldn't
    bs_data_df = bs_data_df.loc[
        (bs_data_df["createdAt"] < (now - timedelta(days=(now.toordinal() % 7) - 1)))
        | bs_data_df["createdAt"].isna()
    ]

    if not include_drafts:
        bs_data_df = bs_data_df[bs_data_df["status"] != "DRAFT"]
    if include_only_dangerous_waste:
        if "wastePop" in bs_data_df.columns:
            bs_data_df = bs_data_df[
                bs_data_df["wasteCode"].str.match(r".*\*$", na=False)
                | bs_data_df["wastePop"]
            ]
        else:
            bs_data_df = bs_data_df[
                bs_data_df["wasteCode"].str.match(r".*\*$", na=False)
            ]

    print(f"get_bs_data duration: {time.time()-started_time} ")

    return bs_data_df


def get_company_data() -> pd.DataFrame:
    """
    Queries the configured database for company data.

    Returns
    -------
    DataFrame
        dataframe of companies for a given period of time, with their creation date
    """
    started_time = time.time()

    sql_query = (SQL_PATH / "get_company_data.sql").read_text()
    company_data_df = pd.read_sql_query(sql_query, con=DB_ENGINE)
    company_data_df["createdAt"] = pd.to_datetime(
        company_data_df["createdAt"], utc=True
    ).dt.tz_convert("Europe/Paris")

    now = datetime.now(tz=ZoneInfo("Europe/Paris")).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    # This is to handle specific case when sqlalchemy does not handle well the timezone
    # and there is data at midnight Paris time the last day of the time window we want to keep
    # that is return by the query but shouldn't
    company_data_df = company_data_df.loc[
        (
            company_data_df["createdAt"]
            < (now - timedelta(days=(now.toordinal() % 7) - 1))
        )
        | company_data_df["createdAt"].isna()
    ]

    print(f"get_company_data duration: {time.time()-started_time} ")

    return company_data_df


def get_user_data() -> pd.DataFrame:
    """
    Queries the configured database for user data, focused on creation date.

    Returns
    --------
    DataFrame
        dataframe of users for a given period of time, with their creation date
    """
    started_time = time.time()

    sql_query = (SQL_PATH / "get_user_data.sql").read_text()
    user_data_df = pd.read_sql_query(sql_query, con=DB_ENGINE)
    user_data_df["createdAt"] = pd.to_datetime(
        user_data_df["createdAt"], utc=True
    ).dt.tz_convert("Europe/Paris")

    now = datetime.now(tz=ZoneInfo("Europe/Paris")).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    # This is to handle specific case when sqlalchemy does not handle well the timezone
    # and there is data at midnight Paris time the last day of the time window we want to keep
    # that is return by the query but shouldn't
    user_data_df = user_data_df.loc[
        (user_data_df["createdAt"] < (now - timedelta(days=(now.toordinal() % 7) - 1)))
        | user_data_df["createdAt"].isna()
    ]

    print(f"get_user_data duration: {time.time()-started_time} ")

    return user_data_df
