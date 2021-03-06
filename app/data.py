"""
Data gathering and processing
"""
import pandas as pd
import sqlalchemy

from app.cache_config import cache_timeout, appcache
from app.time_config import *

# postgresql://admin:admin@localhost:5432/ibnse
engine = sqlalchemy.create_engine(getenv("DATABASE_URL"))


def get_bsdd_created() -> pd.DataFrame:
    """
    Queries the configured database for BSDD data, focused on creation date.
    :return: dataframe of BSDD for a given period of time, with their creation week
    """
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
            'AND "default$default"."Form"."createdAt" < date_trunc(\'week\', CAST(now() '
            "AS timestamp)) "
            # TODO Think of a bedrock starting date to limit number of results
            "ORDER BY createdAt"
        ),
        con=engine,
    )

    # By default the column name is createdat (lowercase), strange
    column_name = df_bsdd_query.columns[0]
    df_bsdd_query.rename(columns={column_name: "createdAt"}, inplace=True)
    return df_bsdd_query


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
        con=engine,
    )

    # By default the column name is processedat, strange
    column_name = df_bsdd_query.columns[0]
    df_bsdd_query.rename(columns={column_name: "processedAt"}, inplace=True)
    return df_bsdd_query


@appcache.memoize(timeout=cache_timeout)
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
        con=engine,
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
        con=engine,
    )
    return df_user_query


def normalize_processing_operation(row) -> str:
    """Replace waste processing codes with readable labels"""
    string = row["recipientProcessingOperation"].upper()
    if string.startswith("R"):
        return "D??chet valoris??"
    elif string.startswith("D"):
        return "D??chet ??limin??"
    return "Autre"


def normalize_quantity_received(row) -> float:
    """Replace weights entered as kg instead of tons"""
    quantity = row["quantityReceived"]
    try:
        if quantity > (int(getenv("SEUIL_DIVISION_QUANTITE")) or 1000):
            quantity = quantity / 1000
    except TypeError:
        print("Error, it's not an int:", quantity)
    return quantity


@appcache.memoize(timeout=cache_timeout)
def get_bsdd_created_df() -> pd.DataFrame:
    today = get_today_datetime()
    df: pd.DataFrame = get_bsdd_created()

    df = df.loc[
        (df["createdAt"] < today)
        & (df["createdAt"] >= get_today_n_days_ago(today))
        ]

    df["createdAt"] = pd.to_datetime(
        df["createdAt"], errors="coerce", utc=True
    )

    df = df.groupby(
        by=["createdAt"], as_index=False
    ).count()
    return df


@appcache.memoize(timeout=cache_timeout)
def get_bsdd_processed_df() -> pd.DataFrame:
    df = get_bsdd_processed()
    df['recipientProcessingOperation'] = df.apply(
        normalize_processing_operation, axis=1
    )
    df['quantityReceived'] = df.apply(normalize_quantity_received, axis=1)
    df["processedAt"] = pd.to_datetime(
        df["processedAt"], errors="coerce", utc=True
    )
    df = df.loc[
        (df["processedAt"] < get_today_datetime())
        & (df["status"] == "PROCESSED")
        ]
    df = df.groupby(
            by=["processedAt", "recipientProcessingOperation"], as_index=False
        ).sum().round()
    return df


# -----------
# ??tablissements et utilisateurs
# -----------

@appcache.memoize(timeout=cache_timeout)
def get_company_user_data_df() -> pd.DataFrame:
    today = get_today_datetime()

    df_company = get_company_data()
    df_company["type"] = "??tablissements"
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
@appcache.memoize(timeout=cache_timeout)
def get_recent_bsdd_created_week() -> pd.DataFrame:
    df = pd.read_sql_query(
        sqlalchemy.text("""
            SELECT date_trunc('week', "default$default"."Form"."createdAt") AS "createdAt", count(*) AS "count"
            FROM "default$default"."Form"
            WHERE ("default$default"."Form"."isDeleted" = FALSE
               AND "default$default"."Form"."createdAt" >= date_trunc('week', CAST((CAST(now() AS timestamp) + (INTERVAL '-20 week')) AS timestamp)) 
               AND "default$default"."Form"."createdAt" < date_trunc('week', CAST(now() AS timestamp)))
            GROUP BY date_trunc('week', "default$default"."Form"."createdAt")
            ORDER BY date_trunc('week', "default$default"."Form"."createdAt")
        """),
        con=engine,
    )

    # By default the column name is createdat (lowercase), strange
    column_name = df.columns[0]
    df.rename(columns={column_name: "createdAt"}, inplace=True)
    return df


# Sent BSDD
@appcache.memoize(timeout=cache_timeout)
def get_recent_bsdd_sent() -> pd.DataFrame:
    df = pd.read_sql_query(
        sqlalchemy.text("""
            SELECT date_trunc('week', "default$default"."Form"."sentAt") AS "sentAt", count(*) AS "count"
            FROM "default$default"."Form"
            WHERE ("default$default"."Form"."isDeleted" = FALSE
               AND "default$default"."Form"."sentAt" >= date_trunc('week', CAST((CAST(now() AS timestamp) + 
               (INTERVAL '-20 week')) AS timestamp)) 
               AND "default$default"."Form"."sentAt" < date_trunc('week', CAST(now() AS timestamp)))
            GROUP BY date_trunc('week', "default$default"."Form"."sentAt")
            ORDER BY date_trunc('week', "default$default"."Form"."sentAt") 
        """),
        con=engine,
    )

    return df


# Received BSDD
@appcache.memoize(timeout=cache_timeout)
def get_recent_bsdd_received() -> pd.DataFrame:
    df = pd.read_sql_query(
        sqlalchemy.text("""
            SELECT date_trunc('week', "default$default"."Form"."receivedAt") AS "receivedAt", count(*) AS "count"
            FROM "default$default"."Form"
            WHERE ("default$default"."Form"."isDeleted" = FALSE
               AND "default$default"."Form"."receivedAt" >= date_trunc('week', CAST((CAST(now() AS timestamp) 
               + (INTERVAL '-20 week')) AS timestamp)) 
               AND "default$default"."Form"."receivedAt" < date_trunc('week', CAST(now() AS timestamp)))
            GROUP BY date_trunc('week', "default$default"."Form"."receivedAt")
            ORDER BY date_trunc('week', "default$default"."Form"."receivedAt")
        """),
        con=engine,
    )

    return df









