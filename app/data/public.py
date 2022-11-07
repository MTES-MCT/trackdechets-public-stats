"""
Data gathering and processing
"""
from datetime import datetime, timedelta
from typing import Tuple
from zoneinfo import ZoneInfo

import pandas as pd

from .data_extract import get_processing_operation_codes_data


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


def get_weekly_waste_quantity_processed_by_operation_code_df(
    bs_data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Creates a DataFrame with total weight of dangerous waste processed by week and by processing operation codes.

    Parameters
    ----------
    bs_data: DataFrame
        DataFrame containing BSx data.

    Returns
    -------
    Series
        Pandas Series containing aggregated data by week. Index are "processed_at" and "processing_operation".
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
        & (bs_data["status"].isin(["PROCESSED", "FOLLOWED_WITH_PNTTD"]))
        & (bs_data["processed_at"] >= "2022-01-03")
        & (
            ~bs_data["processing_operation"].isin(
                [
                    "D9",
                    "D13",
                    "D14",
                    "D15",
                    "R12",
                    "R13",
                    "D 9",
                    "D 13",
                    "D 14",
                    "D 15",
                    "R 12",
                    "R 13",
                ]
            )
        )
    ].copy()

    df = df.groupby(
        by=[
            pd.Grouper(key="processed_at", freq="1W"),
            "processing_operation",
        ]
    )["quantity"].sum()

    return df


def get_waste_quantity_processed_df(
    bsdd_waste_processed_series: pd.Series,
    bsda_waste_processed_series: pd.Series,
    bsff_waste_processed_series: pd.Series,
    bsdasri_waste_processed_series: pd.Series,
) -> pd.DataFrame:
    """Merges the Series of the different types of 'bordereaux' to get an aggregated DataFrame
    with data of all 'bordereaux' summed by week and processing operation code. Also adds the description
    for each processing operation.

    Parameters
    ----------
    bsdd_waste_processed_series: pd.Series
        Pandas Series containing weekly BSDD processed waste data.
    bsda_waste_processed_series: pd.Series
        Pandas Series containing weekly BSDA processed waste data.
    bsff_waste_processed_series: pd.Series
        Pandas Series containing weekly BSFF processed waste data.
    bsdasri_waste_processed_series: pd.Series
        Pandas Series containing weekly BSDASRI processed waste data.

    Returns
    -------
    DataFrame
        Pandas DataFrame containing the aggregated data. Index are 'processed_at' and 'processing_operation'.
    """

    quantity_processed_weekly_df = bsdd_waste_processed_series
    for series in [
        bsda_waste_processed_series,
        bsff_waste_processed_series,
        bsdasri_waste_processed_series,
    ]:
        quantity_processed_weekly_df.add(series, fill_value=0)

    quantity_processed_weekly_df = quantity_processed_weekly_df.reset_index()

    processing_operations_codes_df = get_processing_operation_codes_data()

    quantity_processed_weekly_df = pd.merge(
        quantity_processed_weekly_df,
        processing_operations_codes_df,
        left_on="processing_operation",
        right_on="code",
        how="left",
        validate="many_to_one",
    )

    quantity_processed_weekly_df = quantity_processed_weekly_df.groupby(
        ["processed_at", "processing_operation"]
    ).agg(
        quantity=pd.NamedAgg("quantity", "max"),
        processing_operation_description=pd.NamedAgg("description", "max"),
    )

    return quantity_processed_weekly_df


def get_recovered_and_eliminated_quantity_processed_by_week_series(
    quantity_processed_weekly_df,
) -> Tuple[pd.Series, pd.Series]:
    """Extract the weekly quantity of recovered waste and eliminated waste in two separate Series.

    Parameters
    ----------
    quantity_processed_weekly_df: DataFrame
        DataFrame containing total weight of dangerous waste processed by week and by processing operation codes.

    Returns
    -------
    Tuple of two series
        First element of the tuple is the Series containing the weekly quantity of recovered waste
        and the second one the weekly quantity of eliminated waste.
    """

    res = []

    for regex in [r"^R.*", r"^D.*"]:
        series = (
            quantity_processed_weekly_df.loc[
                quantity_processed_weekly_df.index.get_level_values(
                    "processing_operation"
                ).str.match(regex)
            ]
            .groupby("processed_at")
            .quantity.sum()
            .round()
        )
        res.append(series)

    return res


def get_waste_quantity_processed_by_processing_code_df(
    quantity_processed_weekly_df,
) -> pd.DataFrame:
    """Adds the type of valorisation to the input DataFrame and sum waste quantities to have global quantity by processing operation code.

    Parameters
    ----------
    quantity_processed_weekly_df: DataFrame
        DataFrame containing total weight of dangerous waste processed by week and by processing operation codes.

    Returns
    -------
    DataFrame
        Aggregated quantity of processed weight by processing operation code along with the description of the processing operation
         and type of processing operation.
    """

    agg_data = (
        quantity_processed_weekly_df.groupby("processing_operation", as_index=True)
        .agg(
            quantity=pd.NamedAgg("quantity", "sum"),
            processing_operation_description=pd.NamedAgg(
                "processing_operation_description", "max"
            ),
        )
        .reset_index()
    )

    agg_data["type_operation"] = normalize_processing_operation(
        agg_data["processing_operation"]
    )

    return agg_data
