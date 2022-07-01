"""
Data gathering and processing
"""
from datetime import datetime, timedelta

from zoneinfo import ZoneInfo
import pandas as pd


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
    bsdd_data = bsdd_data[
        (
            bsdd_data["wasteDetailsCode"].str.match(r".*\*$")
            | bsdd_data["wasteDetailsPop"]
        )
    ]
    df = (
        bsdd_data.groupby(by=pd.Grouper(key="createdAt", freq="1W"))
        .count()
        .reset_index()
    )
    return df


# @appcache.memoize(timeout=cache_timeout)
def get_bsdd_processed_df(bsdd_data: pd.DataFrame) -> pd.DataFrame:

    now = datetime.now(tz=ZoneInfo("Europe/Paris")).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    df = bsdd_data[
        (
            bsdd_data["wasteDetailsCode"].str.match(r".*\*$")
            | bsdd_data["wasteDetailsPop"]
        )
        & (
            (
                bsdd_data["processedAt"]
                < (now - timedelta(days=(now.toordinal() % 7) - 1))
            )
            | bsdd_data["processedAt"].isna()
        )
        & (bsdd_data["status"] == "PROCESSED")
        & (bsdd_data["processedAt"] >= "2022-01-01")
    ].copy()
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
