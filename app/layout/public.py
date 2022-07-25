from pathlib import Path
from typing import List

import dash_bootstrap_components as dbc

from app.data.data_extract import get_bs_data, get_company_data, get_user_data
from app.data.public import (
    get_weekly_created_df,
    get_weekly_bs_processed_df,
)
from app.layout.container_factory import create_public_stats_container
from app.layout.figures_factory import (
    create_weekly_quantity_processed_figure,
    create_weekly_created_figure,
)

SQL_PATH = Path.cwd().absolute() / "app/data/sql"


def get_public_stats_container() -> List[dbc.Row]:
    """Create all figures needed for the public stats page
    and returns an Dash HTML layout ready to be displayed.
    """

    # Load all needed data
    bsd_data_df = get_bs_data(
        sql_path=SQL_PATH / "get_bsdd_data.sql",
    )
    bsda_data_df = get_bs_data(
        sql_path=SQL_PATH / "get_bsda_data.sql",
    )
    bsff_data_df = get_bs_data(
        sql_path=SQL_PATH / "get_bsff_data.sql",
    )
    bsdasri_data_df = get_bs_data(
        sql_path=SQL_PATH / "get_bsdasri_data.sql",
    )

    # BSx created weekly figure
    bsdd_created_weekly_df = get_weekly_created_df(
        bsd_data_df,
    )
    bsda_created_weekly_df = get_weekly_created_df(bsda_data_df)
    bsff_created_weekly_df = get_weekly_created_df(bsff_data_df)
    bsdasri_created_weekly_df = get_weekly_created_df(bsdasri_data_df)

    bsdd_created_weekly_fig = create_weekly_created_figure(bsdd_created_weekly_df)
    bsda_created_weekly_fig = create_weekly_created_figure(bsda_created_weekly_df)
    bsff_created_weekly_fig = create_weekly_created_figure(bsff_created_weekly_df)
    bsdasri_created_weekly_fig = create_weekly_created_figure(bsdasri_created_weekly_df)

    bsdd_created_total = bsd_data_df.index.size

    # Waste weight processed weekly

    bsdd_quantity_processed_weekly_df = get_weekly_bs_processed_df(bsd_data_df)
    bsda_quantity_processed_weekly_df = get_weekly_bs_processed_df(bsda_data_df)
    bsff_quantity_processed_weekly_df = get_weekly_bs_processed_df(bsff_data_df)
    bsdasri_quantity_processed_weekly_df = get_weekly_bs_processed_df(bsdasri_data_df)

    quantity_processed_weekly_df = bsdd_quantity_processed_weekly_df
    for df in [
        bsda_quantity_processed_weekly_df,
        bsff_quantity_processed_weekly_df,
        bsdasri_quantity_processed_weekly_df,
    ]:
        quantity_processed_weekly_df.add(df, fill_value=0)

    quantity_recovered = quantity_processed_weekly_df.loc[
        (slice(None), "Déchet valorisé")
    ]
    quantity_destroyed = quantity_processed_weekly_df[(slice(None), "Déchet éliminé")]
    quantity_other = None
    if "Autre" in quantity_processed_weekly_df.index.get_level_values(
        "processingOperation"
    ):
        quantity_other = quantity_processed_weekly_df[(slice(None), "Autre")]

    quantity_processed_weekly_fig = create_weekly_quantity_processed_figure(
        quantity_recovered,
        quantity_destroyed,
        quantity_other,
    )

    quantity_processed_total = quantity_processed_weekly_df.sum()

    company_data_df = get_company_data()
    user_data_df = get_user_data()

    company_created_total = company_data_df[
        company_data_df["createdAt"] >= "2022-01-01"
    ].index.size
    user_created_total = user_data_df[
        user_data_df["createdAt"] >= "2022-01-01"
    ].index.size

    company_created_total_life = company_data_df.index.size
    user_created_total_life = user_data_df.index.size

    company_created_weekly_df = get_weekly_created_df(company_data_df)
    user_created_weekly_df = get_weekly_created_df(user_data_df)

    company_created_weekly = create_weekly_created_figure(company_created_weekly_df)
    user_created_weekly = create_weekly_created_figure(user_created_weekly_df)

    public_stats_container = create_public_stats_container(
        quantity_processed_total,
        bsdd_created_total,
        quantity_processed_weekly_fig,
        bsdd_created_weekly_fig,
        bsda_created_weekly_fig,
        bsff_created_weekly_fig,
        bsdasri_created_weekly_fig,
        company_created_total,
        company_created_total_life,
        user_created_total,
        user_created_total_life,
        company_created_weekly,
        user_created_weekly,
    )
    return public_stats_container
