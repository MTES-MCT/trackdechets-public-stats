"""
Data gathering and processing
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd


def normalize_processing_operation(col: pd.Series) -> pd.Series:
    """Replace, in a Series, waste processing codes with readable labels"""
    regex_dict = {
        r"^R.*": "Déchet valorisé",
        r"^D.*": "Déchet éliminé",
        r"^(?!R|D).*": "Autre",
    }

    return col.replace(regex=regex_dict)


def get_weekly_counts_df(
    data: pd.DataFrame, aggregate_column: str = "created_at"
) -> pd.DataFrame:
    """
    Creates a DataFrame with number of BSx, users, company... created by week.

    Parameters
    ----------
    bs_data: DataFrame
        DataFrame containing BSx data.
    """
    now = datetime.now(tz=ZoneInfo("Europe/Paris"))
    max_date = (now - timedelta(days=now.weekday() + 1)).replace(
        hour=23, minute=59, second=59, microsecond=99
    )
    df = data[data[aggregate_column].between("2022-01-03", max_date)]
    df = (
        df.groupby(by=pd.Grouper(key=aggregate_column, freq="1W"))
        .count()
        .reset_index()
        .rename(columns={aggregate_column: "at"})
    )

    return df


def get_weekly_waste_quantity_processed_df(
    bs_data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Creates a DataFrame with total weight of dangerous waste processed by week.

    Parameters
    ----------
    bs_data: DataFrame
        DataFrame containing BSx data.
    """

    now = datetime.now(tz=ZoneInfo("Europe/Paris")).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    df = bs_data[
        (
            (
                bs_data["processed_at"]
                < (now - timedelta(days=(now.toordinal() % 7) - 1))
            )
            | bs_data["processed_at"].isna()
        )
        & (bs_data["status"] == "PROCESSED")
        & (bs_data["processed_at"] >= "2022-01-03")
    ].copy()

    df["processing_operation"] = normalize_processing_operation(
        df["processing_operation"]
    )

    df = (
        df.groupby(
            by=[
                pd.Grouper(key="processed_at", freq="1W"),
                "processing_operation",
            ]
        )["quantity"]
        .sum()
        .round()
    )

    return df
