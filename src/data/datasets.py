"""This module contains the raw datasets. 
The datasets are loaded in memory to be reusable by other functions.
"""
import pandas as pd

from src.data.data_extract import (
    get_bs_data,
    get_company_data,
    get_user_data,
)


# Load all needed data
BSDD_DATA = get_bs_data(
    "get_bsdd_data.sql",
)
BSDA_DATA = get_bs_data(
    "get_bsda_data.sql",
)
BSFF_DATA = get_bs_data(
    "get_bsff_data.sql",
)
BSDASRI_DATA = get_bs_data(
    "get_bsdasri_data.sql",
)

ALL_BORDEREAUX_DATA = pd.concat([BSDD_DATA, BSDA_DATA, BSFF_DATA, BSDASRI_DATA])

COMPANY_DATA = get_company_data()
USER_DATA = get_user_data()
