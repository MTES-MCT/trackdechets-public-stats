"""This module contains the raw datasets. 
The datasets are loaded in memory to be reusable by other functions.
"""
from datetime import datetime

import polars as pl

from src.data.data_extract import (
    get_bs_data,
    get_company_data,
    get_departement_geographical_data,
    get_naf_nomenclature_data,
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

ALL_BORDEREAUX_DATA = pl.concat(
    [BSDD_DATA, BSDA_DATA, BSFF_DATA, BSDASRI_DATA], how="diagonal"
)

COMPANY_DATA = get_company_data()
USER_DATA = get_user_data()

DEPARTEMENTS_GEOGRAPHICAL_DATA = get_departement_geographical_data()
NAF_NOMENCLATURE_DATA = get_naf_nomenclature_data()

DATA_UPDATE_DATE = datetime.now()
