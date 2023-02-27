"""
Data gathering and processing
"""
import json
import time
from os import environ
from pathlib import Path

import pandas as pd
import polars as pl
import sqlalchemy

from src.data.utils import format_waste_codes

DATABASE_URL = environ["DATABASE_URL"]
DB_ENGINE = sqlalchemy.create_engine(DATABASE_URL)
SQL_PATH = Path(__file__).parent.absolute() / "sql"
STATIC_DATA_PATH = Path(__file__).parent.absolute() / "static"


def get_bs_data(
    query_filename: str,
    include_drafts: bool = False,
    include_only_dangerous_waste: bool = True,
) -> pl.DataFrame:
    """
    Queries the configured database for BSx data. The query should select the columns needed to
    create the figures of the application.

    Parameters
    ----------
    query_filename: str
        Name of the sql query file. Query must select at least a "created_at" column.
    include_drafts: bool
        Wether to include drafts BSx in the result.
    include_only_dangerous_waste: bool
        If true, only 'bordereaux' for dangerous waste are returned.

    Returns
    -------
    DataFrame
        DataFrame of BSx, with all data included in the sql query.
    """

    started_time = time.time()

    sql_query = (SQL_PATH / query_filename).read_text()

    bs_data_df = pl.read_sql(sql_query, connection_uri=DATABASE_URL)

    date_columns = ["created_at", "sent_at", "received_at", "processed_at"]
    bs_data_df = bs_data_df.with_columns(
        [
            pl.col(col_name).dt.with_time_zone(tz="Europe/Paris").dt.offset_by("-1h")
            for col_name in date_columns
        ]
    )

    if not include_drafts:
        bs_data_df = bs_data_df.filter(pl.col("status") != "DRAFT")
    if include_only_dangerous_waste:
        if "waste_pop" in bs_data_df.columns:
            bs_data_df = bs_data_df.filter(
                (pl.col("waste_code").str.contains(pattern=r".*\*$"))
                | pl.col("waste_pop")
            )

        else:
            bs_data_df = bs_data_df.filter(
                pl.col("waste_code").str.contains(pattern=r".*\*$")
            )

    # Depending on the type of 'bordereau', the processing operations codes can contain space or not, so we normalize it :
    bs_data_df = bs_data_df.with_column(
        pl.col("processing_operation").str.replace(r"([RD])([0-9]{1,2})", value="$1 $2")
    )

    print(f"get_bs_data duration: {time.time()-started_time} ")

    return bs_data_df


def get_company_data() -> pl.DataFrame:
    """
    Queries the configured database for company data.

    Returns
    -------
    DataFrame
        DataFrame of companies for a given period of time, with their creation date
    """
    started_time = time.time()

    sql_query = (SQL_PATH / "get_company_data.sql").read_text()
    company_data_df = pl.read_sql(sql_query, connection_uri=DATABASE_URL)

    company_data_df = company_data_df.with_column(
        pl.col("created_at").dt.with_time_zone(tz="Europe/Paris").dt.offset_by("-1h")
    )

    print(f"get_company_data duration: {time.time()-started_time} ")

    return company_data_df


def get_user_data() -> pl.DataFrame:
    """
    Queries the configured database for user data, focused on creation date.

    Returns
    --------
    DataFrame
        dataframe of users for a given period of time, with their creation date
    """
    started_time = time.time()

    sql_query = (SQL_PATH / "get_user_data.sql").read_text()
    user_data_df = pl.read_sql(sql_query, connection_uri=DATABASE_URL)

    user_data_df = user_data_df.with_column(
        pl.col("created_at").dt.with_time_zone(tz="Europe/Paris").dt.offset_by("-1h")
    )

    print(f"get_user_data duration: {time.time()-started_time} ")

    return user_data_df


def get_processing_operation_codes_data() -> pl.DataFrame:
    """
    Returns description for each processing operation codes.

    Returns
    --------
    DataFrame
        DataFrame with processing operations codes and description.
    """
    data = pl.read_sql(
        "SELECT * FROM trusted_zone.codes_operations_traitements",
        connection_uri=DATABASE_URL,
    )

    return data


def get_departement_geographical_data() -> pl.DataFrame:
    """
    Returns INSEE department geographical data.

    Returns
    --------
    DataFrame
        DataFrame with INSEE department geographical data.
    """
    data = pl.read_sql(
        "SELECT * FROM trusted_zone_insee.code_geo_departements",
        connection_uri=DATABASE_URL,
    )

    return data


def get_waste_nomenclature_data() -> pd.DataFrame:
    """
    Returns waste nomenclature data.

    Returns
    --------
    DataFrame
        DataFrame with waste nomenclature data.
    """
    data = pd.read_sql_table(
        table_name="code_dechets", schema="trusted_zone", con=DB_ENGINE
    )
    return data


def get_waste_code_hierarchical_nomenclature() -> list[dict]:
    with (STATIC_DATA_PATH / "waste_codes.json").open() as f:
        waste_code_hierarchy = json.load(f)

    return format_waste_codes(waste_code_hierarchy, add_top_level=True)


def get_naf_nomenclature_data() -> pl.DataFrame:
    data = pl.read_sql(
        "SELECT * FROM trusted_zone_insee.nomenclature_activites_francaises",
        connection_uri=DATABASE_URL,
    )

    return data
