from dash import dcc, html
from feffery_antd_components.AntdTree import AntdTree

from src.data.data_extract import (
    get_departement_geographical_data,
    get_waste_code_hierarchical_nomenclature,
)
from src.data.data_processing import (
    get_recovered_and_eliminated_quantity_processed_by_week_series,
    get_waste_quantity_processed_df,
    get_weekly_waste_quantity_processed_by_operation_code_df,
)
from src.data.datasets import BSDA_DATA, BSDASRI_DATA, BSDD_DATA, BSFF_DATA
from src.data.utils import get_data_date_interval_for_year
from src.pages.figures_factory import create_weekly_quantity_processed_figure


def create_selects():

    geographical_data = get_departement_geographical_data()
    waste_nomenclature = get_waste_code_hierarchical_nomenclature()

    options = (
        geographical_data[["code_departement", "libelle"]]
        .rename(columns={"code_departement": "value", "libelle": "label"})
        .to_dict(orient="records")
    )

    departements_dropdown = html.Div(
        [
            html.Label(
                ["Sélectionner un département :"],
                className="fr-label",
                htmlFor="departement-select",
            ),
            dcc.Dropdown(
                options=options,
                placeholder="Rechercher un département...",
                id="departement-select",
            ),
        ],
        className="fr-select-group",
        id="departement-select-group",
    )

    waste_select = html.Div(
        [
            html.Button(
                ["Filtrer par code déchet"],
                id="waste-select-modal-button",
                className="fr-btn",
                **{"data-fr-opened": False, "aria-controls": "fr-modal-1"}
            ),
            html.Dialog(
                html.Div(
                    html.Div(
                        html.Div(
                            html.Div(
                                [
                                    html.Div(
                                        html.Button(
                                            "Fermer",
                                            className="fr-link--close fr-link",
                                            title="Fermer la fenêtre de sélection des filtres sur les codes déchets",
                                            **{
                                                "aria-controls": "fr-modal-1",
                                            }
                                        ),
                                        className="fr-modal__header",
                                    ),
                                    html.Div(
                                        [
                                            html.H1(
                                                [
                                                    html.Span(
                                                        className="fr-fi-arrow-right-line fr-fi--lg"
                                                    ),
                                                    "Filtrer par code déchets :",
                                                ],
                                                id="fr-modal-title-modal-1",
                                                className="fr-modal__title",
                                            ),
                                            AntdTree(
                                                id="waste-select",
                                                className="waste-select",
                                                treeData=waste_nomenclature,
                                                # multiple=True,
                                                checkable=True,
                                                selectable=False,
                                                defaultCheckedKeys=["all"],
                                                defaultExpandedKeys=["all"],
                                            ),
                                        ],
                                        className="fr-modal__content",
                                    ),
                                ],
                                className="fr-modal__body",
                            ),
                            className="fr-col-12 fr-col-md-8",
                        ),
                        className="fr-grid-row fr-grid-row--center",
                    ),
                    className="fr-container fr-container--fluid fr-container-md",
                ),
                id="fr-modal-1",
                className="fr-modal",
                role="dialog",
                **{"aria-labelledby": "fr-modal-title-modal-1"}
            ),
        ],
        id="waste-select-group",
    )

    selects_div = html.Div(
        [departements_dropdown, waste_select], className="selects-container"
    )

    return selects_div


def create_filtered_waste_processed_figure(
    departement_filter: str, waste_codes_filter: list[str]
):

    bs_data = [BSDD_DATA, BSDA_DATA, BSFF_DATA, BSDASRI_DATA]

    filtered_dfs = []
    for df in bs_data:
        filtered_df = df
        if departement_filter is not None:
            filtered_df = filtered_df[
                filtered_df["destination_departement"] == departement_filter
            ]

        waste_filter_formatted = format_filter(
            filtered_df["waste_code"], waste_codes_filter
        )
        if waste_filter_formatted is not None:

            filtered_df = filtered_df[waste_filter_formatted]
        filtered_dfs.append(filtered_df)

    processed_dfs = []
    for df in filtered_dfs:
        processed_dfs.append(
            get_weekly_waste_quantity_processed_by_operation_code_df(
                df, date_interval=get_data_date_interval_for_year(2022)
            )
        )

    df_processed_waste = get_waste_quantity_processed_df(*processed_dfs)

    (
        df_recovered,
        df_eliminated,
    ) = get_recovered_and_eliminated_quantity_processed_by_week_series(
        df_processed_waste
    )

    fig = create_weekly_quantity_processed_figure(df_recovered, df_eliminated)

    return dcc.Graph(figure=fig)


def format_filter(column_to_filter, waste_codes_filter):

    series_filter = None

    checked = waste_codes_filter["checked"]
    if (checked != ["all"]) and (len(checked) > 0):

        first_level_filters = [e for e in checked if len(e) == 2]
        series_filter = column_to_filter.str[:2].isin(first_level_filters)

        half_checked = waste_codes_filter["half_checked"]
        half_checked = [e for e in half_checked if e != "all"]
        if len(half_checked) != 0:

            half_checked_first_level = [e for e in half_checked if len(e) == 2]
            second_level_filters = [
                e
                for e in checked
                if ((len(e) == 5) and (e[:2] in half_checked_first_level))
            ]
            if len(second_level_filters) > 0:
                series_filter = series_filter | column_to_filter.str[:5].isin(
                    second_level_filters
                )

            half_checked_second_level = [e for e in half_checked if len(e) == 5]
            third_level_filters = [
                e
                for e in checked
                if ((len(e) > 5) and (e[:5] in half_checked_second_level))
            ]
            if len(third_level_filters) > 0:
                series_filter = series_filter | column_to_filter.isin(
                    third_level_filters
                )

    return series_filter
