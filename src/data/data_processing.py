"""
Data gathering and processing
"""
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple
from zoneinfo import ZoneInfo

import pandas as pd
import polars as pl

from .data_extract import get_processing_operation_codes_data


def normalize_processing_operation(value: str) -> pl.Series:
    """Replace, in a Series, waste processing codes with readable labels"""

    if value.startswith("R"):
        return "Déchet valorisé"
    if value.startswith("D"):
        return "Déchet éliminé"

    return "Autre"


def get_weekly_aggregated_series(
    data: pd.DataFrame,
    date_interval: Tuple[datetime, datetime] | None = None,
    aggregate_column: str = "created_at",
    agg_config: Dict[str, str] = {
        "alias": "count",
        "column_name": "id",
        "aggfunc": "count",
    },
    only_non_final_processing_operation: bool | None = None,
) -> pd.DataFrame:
    """
    Creates a DataFrame with number of BSx, users, company... created by week.

    Parameters
    ----------
    bs_data: DataFrame
        DataFrame containing BSx data.
    date_interval: tuple of two datetime objects
        Interval of date used to filter the data as datetime objects.
        First element is the start interval, the second one is the end of the interval.
        The interval is left inclusive.
    aggregate_column: str
        Date column used to group data.
    agg_config: dict
        Dictionary that will be passed to pandas `agg` method in order to perform group operation.
    only_non_final_processing_operation: bool
        If true and `aggregate_column` is equal to "processed_at",
        then only non final processing operation code will be kept in dataset.
        If false and `aggregate_column` is equal to "processed_at",
        then only non final processing operation will be kept in dataset.
        If None, no filtering is applied.

    Returns
    -------
    DataFrame
        Pandas DataFrame containing data aggregated with the given aggregation config.
    """

    if date_interval is not None:
        data = data.filter(
            pl.col(aggregate_column).is_between(*date_interval, closed="left")
        )

    non_final_processing_operation_codes = [
        "D 9",
        "D 13",
        "D 14",
        "D 15",
        "R 12",
        "R 13",
    ]
    match (aggregate_column, only_non_final_processing_operation):
        case ("processed_at", False):
            data = data.filter(
                pl.col("processing_operation")
                .is_in(non_final_processing_operation_codes)
                .is_not()
            )

        case ("processed_at", True):
            data = data.filter(
                pl.col("processing_operation").is_in(
                    non_final_processing_operation_codes
                )
            )

    if agg_config["aggfunc"] == "count":
        agg_expression = (
            pl.col(agg_config["column_name"]).count().alias(agg_config["alias"])
        )
    elif agg_config["aggfunc"] == "sum":
        agg_expression = (
            pl.col(agg_config["column_name"]).sum().alias(agg_config["alias"])
        )
    else:
        raise ValueError("Choose between sum or count aggfunc")

    df = (
        data.with_column(pl.col(aggregate_column).dt.truncate("1w"))
        .sort(aggregate_column)
        .groupby(aggregate_column, maintain_order=True)
        .agg(agg_expression)
        .rename({aggregate_column: "at"})
        .fill_null(0)
    )

    return df


def get_weekly_preprocessed_dfs(
    bs_data: pd.DataFrame, date_interval: tuple[datetime, datetime] | None
) -> Dict[str, List[pd.DataFrame]]:
    """Preprocess raw 'bordereau' data in order to aggregate it at weekly frequency.
    Useful to make several aggregation to prepare data to weekly aggregated figures.

    Parameters
    ----------
    bs_data: DataFrame
        DataFrame containing raw 'bordereau' data.
    date_interval: tuple of two datetime objects
        Interval of date used to filter the data as datetime objects.
        First element is the start interval, the second one is the end of the interval.
        The interval is left inclusive.

    Returns
    -------
    dict
        Dict containing two keys : "counts" and "quantity" representing the two metrics computed,
        Each key is bounded to a list of DataFrames containing the aggregated data for the metric.
        Each item is aggregated by a particular date column.
    """

    bs_datasets = defaultdict(list)
    for aggregate_column, only_non_final_operations in [
        ("created_at", False),
        ("sent_at", False),
        ("received_at", False),
        ("processed_at", None),
        ("processed_at", True),
        ("processed_at", False),
    ]:

        bs_datasets["counts"].append(
            get_weekly_aggregated_series(
                bs_data,
                date_interval,
                aggregate_column,
                only_non_final_processing_operation=only_non_final_operations,
            )
        )
        bs_datasets["quantity"].append(
            get_weekly_aggregated_series(
                bs_data,
                date_interval,
                aggregate_column,
                {
                    "alias": "quantity",
                    "column_name": "quantity",
                    "aggfunc": "sum",
                },
                only_non_final_operations,
            )
        )

    return bs_datasets


def get_weekly_waste_processed_df(
    bs_data: pd.DataFrame, date_interval: tuple[datetime, datetime] | None
) -> pd.Series:
    """
    Creates a Pandas Series with total weight of dangerous waste processed by week.
    Processing operation codes that does not designate final operations are discarded.
    Parameters
    ----------
    bs_data: DataFrame
        DataFrame containing BSx data.
    date_interval: tuple of two datetime objects
        Optional. Interval of date used to filter the data as datetime objects.
        First element is the start interval, the second one is the end of the interval.
        The interval is left inclusive.

    Returns
    -------
    Series
        Pandas Series containing aggregated data by week. Index are "processed_at" and "processing_operation".
    """

    date_filter = bs_data["processed_at"].notna()
    if date_interval is not None:
        date_filter = bs_data["processed_at"].between(*date_interval, inclusive="left")

    df = bs_data[
        date_filter
        & (bs_data["status"].isin(["PROCESSED", "FOLLOWED_WITH_PNTTD"]))
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
    ]

    series = df.groupby(
        by=[
            pd.Grouper(key="processed_at", freq="1W"),
        ]
    )["quantity"].sum()

    return series


def get_weekly_waste_quantity_processed_by_operation_code_df(
    bs_data: pd.DataFrame, date_interval: tuple[datetime, datetime] | None = None
) -> pd.Series:
    """
    Creates a Pandas multi-index Series with total weight of dangerous waste processed by week and by processing operation codes.
    Processing operation codes that does not designate final operations are discarded.
    Parameters
    ----------
    bs_data: DataFrame
        DataFrame containing BSx data.
    date_interval: tuple of two datetime objects
        Optional. Interval of date used to filter the data as datetime objects.
        First element is the start interval, the second one is the end of the interval.
        The interval is left inclusive.

    Returns
    -------
    Series
        Pandas Series containing aggregated data by week. Index are "processed_at" and "processing_operation".
    """
    date_filter = pl.col("processed_at").is_not_null()
    if date_interval is not None:
        date_filter = pl.col("processed_at").is_between(*date_interval, closed="left")

    df = bs_data.filter(
        date_filter
        & pl.col("processing_operation")
        .is_in(
            [
                "D 9",
                "D 13",
                "D 14",
                "D 15",
                "R 12",
                "R 13",
            ]
        )
        .is_not()
        & pl.col("status").is_in(["PROCESSED", "FOLLOWED_WITH_PNTTD"])
    )

    df = (
        df.with_column(pl.col("processed_at").dt.truncate("1w"))
        .sort("processed_at")
        .groupby(["processed_at", "processing_operation"], maintain_order=True)
        .agg(pl.col("quantity").sum())
        .fill_null(0)
    )

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
        quantity_processed_weekly_df = quantity_processed_weekly_df.add(
            series, fill_value=0
        )

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
    quantity_processed_weekly_df: pl.DataFrame,
) -> list[pd.Series]:
    """Extract the weekly quantity of recovered waste and eliminated waste in two separate Series.

    Parameters
    ----------
    quantity_processed_weekly_df: DataFrame
        DataFrame containing total weight of dangerous waste processed by week and by processing operation codes.

    Returns
    -------
    list of two series
        First element is the Series containing the weekly quantity of recovered waste
        and the second one the weekly quantity of eliminated waste.
    """

    res = []

    for regex in [r"^R.*", r"^D.*"]:
        series = (
            quantity_processed_weekly_df.filter(
                pl.col("processing_operation").str.contains(regex)
            )
            .groupby("processed_at", maintain_order=True)
            .agg(pl.col("quantity").sum().round(0))
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

    processing_operations_codes_df = get_processing_operation_codes_data()
    quantity_processed_weekly_df = quantity_processed_weekly_df.join(
        processing_operations_codes_df, left_on="processing_operation", right_on="code"
    )
    agg_data = quantity_processed_weekly_df.groupby("processing_operation").agg(
        [
            pl.col("quantity").sum(),
            pl.col("description").max().alias("processing_operation_description"),
        ]
    )

    agg_data = agg_data.with_column(
        pl.col("processing_operation")
        .apply(lambda x: "Déchet valorisé" if x.startswith("R") else "Déchet éliminé")
        .alias("type_operation")
    )

    return agg_data


def get_company_counts_by_naf_dfs(
    company_data_df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Builds two DataFrames used for the Treemap showing the company counts by company activities (code NAF):
    - The first one is aggregated by "libelle_section", the outermost hierarchical level;
    - The second one is aggregated by "libelle_division", the innermost hierarchical level chosen for the visualization.

    Parameter
    ---------
    company_data_df: DataFrame
        DataFrame containing company data along with NAF data.

    Returns
    -------
    Tuple of two dataframes
        One aggregated by "libelle_section" and one aggregated by "libelle_division".
    """
    company_data_df = company_data_df.with_columns(
        [
            pl.col("libelle_section").fill_null("Section NAF non renseignée."),
            pl.col("libelle_division").fill_null("Division NAF non renseignée."),
            pl.col("code_section").fill_null(""),
            pl.col("code_division").fill_null(""),
        ]
    )

    agg_data_1 = company_data_df.groupby("libelle_section").agg(
        [pl.col("code_section").max(), pl.col("id").count().alias("num_entreprises")]
    )

    agg_data_2 = company_data_df.groupby("libelle_division").agg(
        [
            pl.col("code_division").max(),
            pl.col("libelle_section").max(),
            pl.col("code_section").max(),
            pl.col("id").count().alias("num_entreprises"),
        ]
    )

    return agg_data_1, agg_data_2


def get_total_bs_created(
    all_bordereaux_data: pl.DataFrame,
    date_interval: Tuple[datetime, datetime] | None = None,
) -> int:
    """Returns the total number of 'bordereaux' created.

    Parameters
    ----------
    all_bordereaux_data: DataFrame
        Bordereaux data.
    date_interval: Tuple[datetime, datetime] | None
        Optional, datetime interval as tuple (left inclusive) to filter 'bordereaux' data.

    Returns
    -------
    int
        Total number of 'bordereaux' created.

    """
    bs_created_total = 0

    if date_interval is not None:
        bs_created_total = all_bordereaux_data.filter(
            pl.col("created_at").is_between(*date_interval, closed="left")
        ).height
    else:
        bs_created_total = all_bordereaux_data.height

    return bs_created_total


def get_total_quantity_processed(
    all_bordereaux_data: pl.DataFrame,
    date_interval: Tuple[datetime, datetime] | None = None,
) -> int:
    """Returns the total quantity processed (only final processing operation codes).

    Parameters
    ----------
    all_bordereaux_data: DataFrame
        Bordereaux data.
    date_interval: Tuple[datetime, datetime] | None
        Optional, datetime interval as tuple (left inclusive) to filter 'bordereaux' data.

    Returns
    -------
    float
        Total quantity processed.

    """
    quantity_processed_total = 0
    if date_interval is not None:
        quantity_processed_total = (
            all_bordereaux_data.filter(
                pl.col("created_at").is_between(*date_interval, closed="left")
                & pl.col("processing_operation")
                .is_in(
                    [
                        "D 9",
                        "D 13",
                        "D 14",
                        "D 15",
                        "R 12",
                        "R 13",
                    ]
                )
                .is_not()
            )
            .select("quantity")
            .sum()
            .item()
        )
    else:
        quantity_processed_total = (
            all_bordereaux_data.filter(
                pl.col("processing_operation")
                .is_in(
                    [
                        "D 9",
                        "D 13",
                        "D 14",
                        "D 15",
                        "R 12",
                        "R 13",
                    ]
                )
                .is_not()
            )
            .select("quantity")
            .sum()
            .item()
        )

    return quantity_processed_total
