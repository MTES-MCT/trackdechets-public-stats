#######################################################################################################
#
#                       Internal statistics
#
#######################################################################################################
from os import getenv
from pathlib import Path

import pandas as pd
import sqlalchemy

from app.time_config import *

# postgresql://admin:admin@localhost:5432/ibnse
DB_ENGINE = sqlalchemy.create_engine(getenv("DATABASE_URL"))
SQL_PATH = Path("app/sql")

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
