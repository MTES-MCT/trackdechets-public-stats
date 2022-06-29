"""
Data gathering and processing
"""
from pathlib import Path
from zoneinfo import ZoneInfo
from datetime import datetime
import time
import pandas as pd
import sqlalchemy

from app.time_config import *
from app.cache_config import appcache

# postgresql://admin:admin@localhost:5432/ibnse
DB_ENGINE = sqlalchemy.create_engine(getenv("DATABASE_URL"))
SQL_PATH = Path("app/sql")


def get_bsdd_data() -> pd.DataFrame:

    started_time = time.time()
    sql_query = (SQL_PATH / "get_bsdd_data.sql").read_text()
    bsdd_data_df = pd.read_sql_query(sql_query, con=DB_ENGINE)
    bsdd_data_df["createdAt"] = pd.to_datetime(
        bsdd_data_df["createdAt"], utc=True
    ).dt.tz_convert("Europe/Paris")
    bsdd_data_df["processedAt"] = pd.to_datetime(
        bsdd_data_df["processedAt"], utc=True, errors="coerce"
    ).dt.tz_convert("Europe/Paris")
    print(f"get_bsdd_data duration: {time.time()-started_time} ")

    return bsdd_data_df


def get_bsdd_created() -> pd.DataFrame:
    """
    Queries the configured database for BSDD data, focused on creation date.
    :return: dataframe of BSDD for a given period of time, with their creation week
    """
    print("get_bsdd_created called")
    df_bsdd_query = pd.read_sql_query(
        sqlalchemy.text(
            "SELECT "
            'date_trunc(\'week\', "default$default"."Form"."createdAt") AS createdAt, '
            # Need id to receive count values upon groupBy
            "id "
            'FROM "default$default"."Form" '
            "WHERE "
            '"Form"."isDeleted" = FALSE AND "Form"."status" <> \'DRAFT\' '
            # To keep only dangerous waste at query level:
            'AND ("default$default"."Form"."wasteDetailsCode" LIKE \'%*%\' '
            'OR "default$default"."Form"."wasteDetailsPop" = TRUE)'
            'AND "default$default"."Form"."createdAt" >= date_trunc(\'week\','
            f"CAST((CAST(now() AS timestamp) + (INTERVAL '-{str(time_delta_m)} month'))"
            "AS timestamp))"
            'and cast("default$default"."Form"."processedAt" as date) >= \'2022-01-01\''
            'AND "default$default"."Form"."createdAt" < date_trunc(\'week\', CAST(now() '
            "AS timestamp)) "
            # @TODO Think of a bedrock starting date to limit number of results
            "ORDER BY createdAt"
        ),
        con=DB_ENGINE,
    )

    # By default the column name is createdat (lowercase), strange
    column_name = df_bsdd_query.columns[0]
    df_bsdd_query.rename(columns={column_name: "createdAt"}, inplace=True)
    return df_bsdd_query


# deprecated
def get_bsdd_processed() -> pd.DataFrame:
    """
    Queries the configured database for BSDD data, focused on processing date.
    :return: dataframe of BSDD for a given period of time, with their processing week
    """
    df_bsdd_query = pd.read_sql_query(
        sqlalchemy.text(
            "SELECT "
            'date_trunc(\'week\', "default$default"."Form"."processedAt") AS processedAt, '
            '"Form"."status",'
            '"Form"."quantityReceived", '
            '"Form"."recipientProcessingOperation" '
            'FROM "default$default"."Form" '
            "WHERE "
            '"Form"."isDeleted" = FALSE AND "Form"."status" <> \'DRAFT\' '
            # To keep only dangerous waste at query level:
            'AND "default$default"."Form"."processedAt" >= date_trunc(\'week\','
            f"CAST((CAST(now() AS timestamp) + (INTERVAL '-{str(time_delta_m)} month'))"
            " AS timestamp))"
            'AND ("default$default"."Form"."wasteDetailsCode" LIKE \'%*%\' '
            'OR "default$default"."Form"."wasteDetailsPop" = TRUE)'
            'AND "default$default"."Form"."processedAt" < date_trunc(\'week\', CAST(now() AS timestamp)) '
            "ORDER BY processedAt"
        ),
        con=DB_ENGINE,
    )

    # By default the column name is processedat, strange
    column_name = df_bsdd_query.columns[0]
    df_bsdd_query.rename(columns={column_name: "processedAt"}, inplace=True)
    return df_bsdd_query


# @appcache.memoize(timeout=10)
def get_company_data() -> pd.DataFrame:
    """
    Queries the configured database for company data.
    :return: dataframe of companies for a given period of time, with their creation week
    """
    df_company_query = pd.read_sql_query(
        'SELECT id, date_trunc(\'week\', "default$default"."Company"."createdAt") AS "createdAt" '
        'FROM "default$default"."Company" '
        'WHERE "default$default"."Company"."createdAt" < date_trunc(\'week\', CAST(now() AS timestamp)) '
        'ORDER BY date_trunc(\'week\', "default$default"."Company"."createdAt")',
        con=DB_ENGINE,
    )
    return df_company_query


def get_user_data() -> pd.DataFrame:
    """
    Queries the configured database for user data, focused on creation date.
    :return: dataframe of users for a given period of time, with their creation week
    """
    df_user_query = pd.read_sql_query(
        'SELECT id, date_trunc(\'week\', "default$default"."User"."createdAt") AS "createdAt" '
        'FROM "default$default"."User" '
        'WHERE "User"."isActive" = True '
        'AND "default$default"."User"."createdAt" < date_trunc(\'week\', CAST(now() AS timestamp)) '
        'ORDER BY date_trunc(\'week\', "default$default"."User"."createdAt")',
        con=DB_ENGINE,
    )
    return df_user_query


def normalize_processing_operation(col: pd.Series) -> pd.Series:
    """Replace waste processing codes with readable labels"""
    regex_dict = {
        r"^R.*": "Déchet valorisé",
        r"^D.*": "Déchet éliminé",
        r"^(?!R|D).*": "Autre",
    }

    return col.replace(regex=regex_dict)


def normalize_quantity_received(row) -> float:
    """Replace weights entered as kg instead of tons"""
    quantity = row["quantityReceived"]
    try:
        if quantity > (int(getenv("SEUIL_DIVISION_QUANTITE")) or 1000):
            quantity = quantity / 1000
    except TypeError:
        print("Error, it's not an int:", quantity)
    return quantity


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
    # @todo Optimize this normalization as it takes 65% of function time
    df["quantityReceived"] = df.apply(normalize_quantity_received, axis=1)
    now = datetime.now(tz=ZoneInfo("Europe/Paris"))
    df = df.loc[
        (df["processedAt"] < now - timedelta(days=now.toordinal() % 7))
        & (df["status"] == "PROCESSED")
    ]
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
def get_company_user_data_df() -> pd.DataFrame:
    today = get_today_datetime()

    df_company = get_company_data()
    df_company["type"] = "Établissements"
    df_company["createdAt"] = pd.to_datetime(df_company["createdAt"], utc=True)

    df_user = get_user_data()
    df_user["type"] = "Utilisateurs"
    df_user["createdAt"] = pd.to_datetime(df_user["createdAt"], utc=True)
    # Concatenate user and company data
    df_company_user_created = pd.concat([df_company, df_user], ignore_index=True)

    df_company_user_created = df_company_user_created.loc[
        (today > df_company_user_created["createdAt"])
        & (df_company_user_created["createdAt"] >= get_today_n_days_ago(today))
    ]
    df_company_user_created_grouped = df_company_user_created.groupby(
        by=["type", "createdAt"], as_index=False
    ).count()
    return df_company_user_created_grouped


#######################################################################################################
#
#                       Internal statistics
#
#######################################################################################################

# Created BSDD
# @appcache.memoize(timeout=cache_timeout)
def get_recent_bsdd_created_week() -> pd.DataFrame:
    df = pd.read_sql_query(
        sqlalchemy.text(
            """
            SELECT date_trunc('week', "default$default"."Form"."createdAt") AS "createdAt", count(*) AS "count"
            FROM "default$default"."Form"
            WHERE ("default$default"."Form"."isDeleted" = FALSE
               AND "default$default"."Form"."createdAt" >= date_trunc('week', CAST((CAST(now() AS timestamp) + (INTERVAL '-20 week')) AS timestamp)) 
               AND "default$default"."Form"."createdAt" < date_trunc('week', CAST(now() AS timestamp)))
            GROUP BY date_trunc('week', "default$default"."Form"."createdAt")
            ORDER BY date_trunc('week', "default$default"."Form"."createdAt")
        """
        ),
        con=DB_ENGINE,
    )

    # By default the column name is createdat (lowercase), strange
    column_name = df.columns[0]
    df.rename(columns={column_name: "createdAt"}, inplace=True)
    return df


# Sent BSDD
# @appcache.memoize(timeout=cache_timeout)
def get_recent_bsdd_sent() -> pd.DataFrame:
    df = pd.read_sql_query(
        sqlalchemy.text(
            """
            SELECT date_trunc('week', "default$default"."Form"."sentAt") AS "sentAt", count(*) AS "count"
            FROM "default$default"."Form"
            WHERE ("default$default"."Form"."isDeleted" = FALSE
               AND "default$default"."Form"."sentAt" >= date_trunc('week', CAST((CAST(now() AS timestamp) + 
               (INTERVAL '-20 week')) AS timestamp)) 
               AND "default$default"."Form"."sentAt" < date_trunc('week', CAST(now() AS timestamp)))
            GROUP BY date_trunc('week', "default$default"."Form"."sentAt")
            ORDER BY date_trunc('week', "default$default"."Form"."sentAt") 
        """
        ),
        con=DB_ENGINE,
    )

    return df


# Received BSDD
# @appcache.memoize(timeout=cache_timeout)
def get_recent_bsdd_received() -> pd.DataFrame:
    df = pd.read_sql_query(
        sqlalchemy.text(
            """
            SELECT date_trunc('week', "default$default"."Form"."receivedAt") AS "receivedAt", count(*) AS "count"
            FROM "default$default"."Form"
            WHERE ("default$default"."Form"."isDeleted" = FALSE
               AND "default$default"."Form"."receivedAt" >= date_trunc('week', CAST((CAST(now() AS timestamp) 
               + (INTERVAL '-20 week')) AS timestamp)) 
               AND "default$default"."Form"."receivedAt" < date_trunc('week', CAST(now() AS timestamp)))
            GROUP BY date_trunc('week', "default$default"."Form"."receivedAt")
            ORDER BY date_trunc('week', "default$default"."Form"."receivedAt")
        """
        ),
        con=DB_ENGINE,
    )

    return df
