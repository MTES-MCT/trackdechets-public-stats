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


def get_weekly_bs_created_df(bs_data: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a DataFrame with number of BSx created by week.

    Parameters
    ----------
    bs_data: DataFrame
        DataFrame containing BSx data.
    """

    df = (
        bs_data.groupby(by=pd.Grouper(key="createdAt", freq="1W")).count().reset_index()
    )

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


# -----------
# Établissements et utilisateurs
# -----------


def get_company_user_data_df(
    company_data: pd.DataFrame, user_data: pd.DataFrame
) -> pd.DataFrame:
    """
    Creates a DataFrame with number of users and companies created by week.

    Parameters
    ----------
    company_data: DataFrame
        DataFrame containing companies data.
    user_data: DataFrame
        DataFrame containing user data.
    """

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
