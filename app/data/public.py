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


def get_bsdd_data() -> pd.DataFrame:
    """
    Queries the configured database for BSDD data.
    :return: dataframe of BSDD for a given period of time, with their creation date
    """

    started_time = time.time()

    sql_query = (SQL_PATH / "get_bsdd_data.sql").read_text()
    bsdd_data_df = pd.read_sql_query(
        sql_query,
        con=DB_ENGINE,
    )
    bsdd_data_df["createdAt"] = pd.to_datetime(
        bsdd_data_df["createdAt"], utc=True
    ).dt.tz_convert("Europe/Paris")
    bsdd_data_df["processedAt"] = pd.to_datetime(
        bsdd_data_df["processedAt"], utc=True, errors="coerce"
    ).dt.tz_convert("Europe/Paris")

    now = datetime.now(tz=ZoneInfo("Europe/Paris")).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    # This is to handle specific case when sqlalchemy does not handle well the timezone
    # and there is data at midnight Paris time the last day of the time window we want to keep
    # that is return by the query but shouldn't
    bsdd_data_df = bsdd_data_df.loc[
        (
            (
                bsdd_data_df["processedAt"]
                < (now - timedelta(days=(now.toordinal() % 7) - 1))
            )
            | bsdd_data_df["processedAt"].isna()
        )
        & (
            (
                bsdd_data_df["createdAt"]
                < (now - timedelta(days=(now.toordinal() % 7) - 1))
            )
            | bsdd_data_df["createdAt"].isna()
        )
    ]

    print(f"get_bsdd_data duration: {time.time()-started_time} ")

    return bsdd_data_df


# @appcache.memoize(timeout=10)
def get_company_data() -> pd.DataFrame:
    """
    Queries the configured database for company data.
    :return: dataframe of companies for a given period of time, with their creation date
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
    :return: dataframe of users for a given period of time, with their creation date
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


def normalize_processing_operation(col: pd.Series) -> pd.Series:
    """Replace waste processing codes with readable labels"""
    regex_dict = {
        r"^R.*": "Déchet valorisé",
        r"^D.*": "Déchet éliminé",
        r"^(?!R|D).*": "Autre",
    }

    return col.replace(regex=regex_dict)


# @appcache.memoize(timeout=cache_timeout)
def get_bsdd_created_df(bsdd_data: pd.DataFrame) -> pd.DataFrame:

    df = (
        bsdd_data.groupby(by=pd.Grouper(key="createdAt", freq="1W"))
        .count()
        .reset_index()
    )
    return df


# @appcache.memoize(timeout=cache_timeout)
def get_bsdd_processed_df(bsdd_data: pd.DataFrame) -> pd.DataFrame:
    df = bsdd_data.copy()
    df["recipientProcessingOperation"] = normalize_processing_operation(
        df["recipientProcessingOperation"]
    )

    df = (
        df.groupby(
            by=[
                pd.Grouper(key="processedAt", freq="1W"),
                "recipientProcessingOperation",
            ]
        )
        .sum()
        .round()
    ).reset_index()

    return df


# -----------
# Établissements et utilisateurs
# -----------


# @appcache.memoize(timeout=cache_timeout)
def get_company_user_data_df(
    company_data: pd.DataFrame, user_data: pd.DataFrame
) -> pd.DataFrame:

    df_company = company_data.copy()
    df_company["type"] = "Établissements"

    df_user = user_data.copy()
    df_user["type"] = "Utilisateurs"
    # Concatenate user and company data
    df_company_user_created = pd.concat([df_company, df_user], ignore_index=True)

    df_company_user_created = df_company_user_created.loc[
        df_company_user_created["createdAt"] >= "2022-01-01"
    ]
    df_company_user_created_grouped = (
        df_company_user_created.groupby(
            by=["type", pd.Grouper(key="createdAt", freq="1W")]
        )
        .count()
        .reset_index()
    )
    return df_company_user_created_grouped
