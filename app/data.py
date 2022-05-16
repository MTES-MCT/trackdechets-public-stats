"""
Data gathering and processing
"""
import pandas as pd
import sqlalchemy

from app.cache_config import cache_timeout, appcache
from app.time_config import *

# postgresql://admin:admin@localhost:5432/ibnse
engine = sqlalchemy.create_engine(getenv("DATABASE_URL"))


@appcache.memoize(timeout=cache_timeout)
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


@appcache.memoize(timeout=cache_timeout)
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


@appcache.memoize(timeout=cache_timeout)
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
        return "Déchet valorisé"
    elif string.startswith("D"):
        return "Déchet éliminé"
    return "Autre"


def normalize_quantity_received(row) -> float:
    """Replace weights entered as kg instead of tons"""
    quantity = row["quantityReceived"]
    if quantity > (int(getenv("SEUIL_DIVISION_QUANTITE")) or 1000):
        quantity = quantity / 1000
    return quantity


# TODO Currenty only the get_blabla_data functions are cached, which means
#  only the db calls are cached.
# Not the dataframe postprocessing, which is always done. Dataframe postprocessing could
# be added to those functions.

df_bsdd_created: pd.DataFrame = get_bsdd_created()
df_bsdd_processed: pd.DataFrame = get_bsdd_processed()

df_bsdd_created = df_bsdd_created.loc[
    (df_bsdd_created["createdAt"] < today)
    & (df_bsdd_created["createdAt"] >= date_n_days_ago)
    ]

df_bsdd_processed["recipientProcessingOperation"] = df_bsdd_processed.apply(
    normalize_processing_operation, axis=1
)
df_bsdd_processed["quantityReceived"] = df_bsdd_processed.apply(
    normalize_quantity_received, axis=1
)
df_bsdd_created["createdAt"] = pd.to_datetime(
    df_bsdd_created["createdAt"], errors="coerce", utc=True
)
df_bsdd_processed["processedAt"] = pd.to_datetime(
    df_bsdd_processed["processedAt"], errors="coerce", utc=True
)

df_bsdd_created_grouped = df_bsdd_created.groupby(
    by=["createdAt"], as_index=False
).count()

df_bsdd_processed = df_bsdd_processed.loc[
    (df_bsdd_processed["processedAt"] < today)
    & (df_bsdd_processed["status"] == "PROCESSED")
    ]
df_bsdd_processed_grouped = (
    df_bsdd_processed.groupby(
        by=["processedAt", "recipientProcessingOperation"], as_index=False
    ).sum().round()
)

# -----------
# Établissements et utilisateurs
# -----------

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
    & (df_company_user_created["createdAt"] >= date_n_days_ago)
    ]
df_company_user_created_grouped = df_company_user_created.groupby(
    by=["type", "createdAt"], as_index=False
).count()


#######################################################################################################
#
#                       Internal statistics
#
#######################################################################################################

@appcache.memoize(timeout=cache_timeout)
def get_recent_bsdd_created() -> pd.DataFrame:
    """
    Queries the configured database for BSDD data, focused on creation date.
    :return: dataframe of BSDD for a given period of time, with their creation week
    """
    df = pd.read_sql_query(
        sqlalchemy.text("""
            SELECT date_trunc('week', "default$default"."Form"."createdAt") AS "createdAt"
            FROM "default$default"."Form"
            WHERE ("default$default"."Form"."isDeleted" = FALSE
               AND "default$default"."Form"."createdAt" >= '2022-01-01'
               AND "default$default"."Form"."createdAt" < date_trunc('week', CAST(now() AS timestamp)))
        """),
        con=engine,
    )

    # By default the column name is createdat (lowercase), strange
    column_name = df.columns[0]
    df.rename(columns={column_name: "createdAt"}, inplace=True)
    return df


@appcache.memoize(timeout=cache_timeout)
def get_recent_bsdd_created() -> pd.DataFrame:
    """
    Queries the configured database for BSDA data, focused on creation date.
    :return: dataframe of BSDA for a given period of time, with their creation week
    """
    df = pd.read_sql_query(
        sqlalchemy.text("""
            SELECT "Bsda"."id", "Bsda"."createdAt",
            "Bsda"."transporterTransportTakenOverAt",
            "Bsda"."destinationOperationDate"
            FROM "default$default"."Bsda"
            WHERE (
            "default$default"."Bsda"."createdAt" >= '2022-01-01'
               AND "default$default"."Bsda"."createdAt" < date_trunc('week', CAST(now() AS timestamp)) 
               AND "default$default"."Bsda"."isDeleted" = FALSE)
        """),
        con=engine,
    )

    # By default the column name is createdat (lowercase), strange
    column_name = df.columns[0]
    df.rename(columns={column_name: "createdAt"}, inplace=True)
    return df




