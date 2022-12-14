from pathlib import Path
from typing import List

import dash_bootstrap_components as dbc

from app.data.data_extract import get_bs_data, get_company_data, get_user_data
from app.data.public import (
    get_recovered_and_eliminated_quantity_processed_by_week_series,
    get_waste_quantity_processed_df,
    get_weekly_counts_df,
    get_weekly_waste_quantity_processed_by_operation_code_df,
    get_waste_quantity_processed_by_processing_code_df,
    get_company_counts_by_naf_dfs,
)
from app.layout.container_factory import create_public_stats_container
from app.layout.figures_factory import (
    create_quantity_processed_sunburst_figure,
    create_weekly_quantity_processed_figure,
    create_weekly_counts_scatter_figure,
    create_weekly_created_figure,
    create_treemap_companies_figure,
)

SQL_PATH = Path.cwd().absolute() / "app/data/sql"


def get_public_stats_container() -> List[dbc.Row]:
    """Create all figures needed for the public stats page
    and returns an Dash HTML layout ready to be displayed.
    """

    # Load all needed data
    bsdd_data_df = get_bs_data(
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
    bsdd_created_weekly_df = get_weekly_counts_df(
        bsdd_data_df,
    )
    bsda_created_weekly_df = get_weekly_counts_df(bsda_data_df)
    bsff_created_weekly_df = get_weekly_counts_df(bsff_data_df)
    bsdasri_created_weekly_df = get_weekly_counts_df(bsdasri_data_df)

    # BSx sent weekly figure
    bsdd_sent_weekly_df = get_weekly_counts_df(bsdd_data_df, aggregate_column="sent_at")
    bsda_sent_weekly_df = get_weekly_counts_df(bsda_data_df, aggregate_column="sent_at")
    bsff_sent_weekly_df = get_weekly_counts_df(bsff_data_df, aggregate_column="sent_at")
    bsdasri_sent_weekly_df = get_weekly_counts_df(
        bsdasri_data_df, aggregate_column="sent_at"
    )

    # BSx received weekly figure
    bsdd_received_weekly_df = get_weekly_counts_df(
        bsdd_data_df, aggregate_column="received_at"
    )
    bsda_received_weekly_df = get_weekly_counts_df(
        bsda_data_df, aggregate_column="received_at"
    )
    bsff_received_weekly_df = get_weekly_counts_df(
        bsff_data_df, aggregate_column="received_at"
    )
    bsdasri_received_weekly_df = get_weekly_counts_df(
        bsdasri_data_df, aggregate_column="received_at"
    )

    # BSx processed weekly figure
    bsdd_processed_weekly_df = get_weekly_counts_df(
        bsdd_data_df, aggregate_column="processed_at"
    )
    bsda_processed_weekly_df = get_weekly_counts_df(
        bsda_data_df, aggregate_column="processed_at"
    )
    bsff_processed_weekly_df = get_weekly_counts_df(
        bsff_data_df, aggregate_column="processed_at"
    )
    bsdasri_processed_weekly_df = get_weekly_counts_df(
        bsdasri_data_df, aggregate_column="processed_at"
    )

    bsdd_counts_weekly_fig = create_weekly_counts_scatter_figure(
        bsdd_created_weekly_df,
        bsdd_sent_weekly_df,
        bsdd_received_weekly_df,
        bsdd_processed_weekly_df,
    )
    bsda_counts_weekly_fig = create_weekly_counts_scatter_figure(
        bsda_created_weekly_df,
        bsda_sent_weekly_df,
        bsda_received_weekly_df,
        bsda_processed_weekly_df,
    )
    bsff_counts_weekly_fig = create_weekly_counts_scatter_figure(
        bsff_created_weekly_df,
        bsff_sent_weekly_df,
        bsff_received_weekly_df,
        bsff_processed_weekly_df,
    )
    bsdasri_counts_weekly_fig = create_weekly_counts_scatter_figure(
        bsdasri_created_weekly_df,
        bsdasri_sent_weekly_df,
        bsdasri_received_weekly_df,
        bsdasri_processed_weekly_df,
    )

    # Waste weight processed weekly

    bsdd_quantity_processed_weekly_series = (
        get_weekly_waste_quantity_processed_by_operation_code_df(bsdd_data_df)
    )
    bsda_quantity_processed_weekly_series = (
        get_weekly_waste_quantity_processed_by_operation_code_df(bsda_data_df)
    )
    bsff_quantity_processed_weekly_series = (
        get_weekly_waste_quantity_processed_by_operation_code_df(bsff_data_df)
    )
    bsdasri_quantity_processed_weekly_series = (
        get_weekly_waste_quantity_processed_by_operation_code_df(bsdasri_data_df)
    )

    quantity_processed_weekly_df = get_waste_quantity_processed_df(
        bsdd_quantity_processed_weekly_series,
        bsda_quantity_processed_weekly_series,
        bsff_quantity_processed_weekly_series,
        bsdasri_quantity_processed_weekly_series,
    )

    # Total bordereaux created
    bs_created_total = 0
    for df in [bsdd_data_df, bsda_data_df, bsff_data_df, bsdasri_data_df]:
        bs_created_total += df.index.size

    # Waste weight processed weekly

    (
        recovered_quantity_series,
        eliminated_quantity_series,
    ) = get_recovered_and_eliminated_quantity_processed_by_week_series(
        quantity_processed_weekly_df
    )
    quantity_processed_weekly_fig = create_weekly_quantity_processed_figure(
        recovered_quantity_series, eliminated_quantity_series
    )

    waste_quantity_processed_by_processing_code_df = (
        get_waste_quantity_processed_by_processing_code_df(quantity_processed_weekly_df)
    )

    quantity_processed_sunburst_fig = create_quantity_processed_sunburst_figure(
        waste_quantity_processed_by_processing_code_df
    )

    quantity_processed_total = quantity_processed_weekly_df["quantity"].sum()

    company_data_df = get_company_data()
    user_data_df = get_user_data()

    company_created_total_life = company_data_df.index.size
    user_created_total_life = user_data_df.index.size

    company_created_weekly_df = get_weekly_counts_df(company_data_df)
    user_created_weekly_df = get_weekly_counts_df(user_data_df)

    company_created_weekly = create_weekly_created_figure(company_created_weekly_df)
    user_created_weekly = create_weekly_created_figure(user_created_weekly_df)

    (
        company_counts_by_section,
        company_counts_by_division,
    ) = get_company_counts_by_naf_dfs(company_data_df)
    treemap_companies_figure = create_treemap_companies_figure(
        company_counts_by_section, company_counts_by_division
    )
    public_stats_container = create_public_stats_container(
        quantity_processed_total,
        bs_created_total,
        quantity_processed_weekly_fig,
        quantity_processed_sunburst_fig,
        bsdd_counts_weekly_fig,
        bsda_counts_weekly_fig,
        bsff_counts_weekly_fig,
        bsdasri_counts_weekly_fig,
        company_created_total_life,
        user_created_total_life,
        company_created_weekly,
        user_created_weekly,
        treemap_companies_figure,
    )
    return public_stats_container
