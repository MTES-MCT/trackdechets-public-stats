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


def get_weekly_created_df(data: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a DataFrame with number of BSx, users, company... created by week.

    Parameters
    ----------
    bs_data: DataFrame
        DataFrame containing BSx data.
    """

    df = data.groupby(by=pd.Grouper(key="createdAt", freq="1W")).count().reset_index()

    return df


def get_weekly_bs_processed_df(
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
            (bs_data["processedAt"] < (now - timedelta(days=(now.toordinal() % 7) - 1)))
            | bs_data["processedAt"].isna()
        )
        & (bs_data["status"] == "PROCESSED")
        & (bs_data["processedAt"] >= "2022-01-01")
    ].copy()

    df["processingOperation"] = normalize_processing_operation(
        df["processingOperation"]
    )

    df = (
        df.groupby(
            by=[
                pd.Grouper(key="processedAt", freq="1W"),
                "processingOperation",
            ]
        )["weightValue"]
        .sum()
        .round()
    )

    return df
