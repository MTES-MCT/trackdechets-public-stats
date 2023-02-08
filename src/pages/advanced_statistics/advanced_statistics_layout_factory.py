from datetime import datetime
from zoneinfo import ZoneInfo

from dash import dcc, html, no_update
from feffery_antd_components.AntdTree import AntdTree

from src.data.data_extract import (
    get_departement_geographical_data,
    get_waste_code_hierarchical_nomenclature,
)
from src.data.data_processing import (
    get_recovered_and_eliminated_quantity_processed_by_week_series,
    get_weekly_waste_quantity_processed_by_operation_code_df,
)
from src.data.datasets import ALL_BORDEREAUX_DATA
from src.data.utils import get_data_date_interval_for_year
from src.pages.advanced_statistics.utils import format_filter
from src.pages.figures_factory import create_weekly_quantity_processed_figure
from src.pages.utils import add_callout


def create_filter_selects() -> html.Div:

    geographical_data = get_departement_geographical_data()
    waste_nomenclature = get_waste_code_hierarchical_nomenclature()

    options = (
        geographical_data[["code_departement", "libelle"]]
        .rename(columns={"code_departement": "value", "libelle": "label"})
        .to_dict(orient="records")
    )

    options.insert(0, {"value": "all", "label": "France entière"})

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
                value="all",
                clearable=False,
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
                **{"data-fr-opened": False, "aria-controls": "fr-modal-1"},
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
                                            },
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
                **{"aria-labelledby": "fr-modal-title-modal-1"},
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
    geographical_data = get_departement_geographical_data()
    bs_data = ALL_BORDEREAUX_DATA

    departement_filter_str = ""

    bs_data_filtered = bs_data
    if (departement_filter is not None) and (departement_filter != "all"):
        departement_filter_str = (
            "- "
            + geographical_data.loc[
                geographical_data["code_departement"] == departement_filter,
                "libelle",
            ].item()
        )
        bs_data_filtered = bs_data[
            bs_data["destination_departement"] == departement_filter
        ]

    waste_filter_formatted = format_filter(
        bs_data_filtered["waste_code"], waste_codes_filter
    )
    if waste_filter_formatted is not None:

        bs_data_filtered = bs_data_filtered[waste_filter_formatted]

    date_interval = (
        datetime(2022, 1, 3, tzinfo=ZoneInfo("Europe/Paris")),
        datetime.now(tz=ZoneInfo("Europe/Paris")),
    )
    bs_data_filtered_grouped = get_weekly_waste_quantity_processed_by_operation_code_df(
        bs_data_filtered,
        date_interval,
    )

    (
        df_recovered,
        df_eliminated,
    ) = get_recovered_and_eliminated_quantity_processed_by_week_series(
        bs_data_filtered_grouped.to_frame()
    )

    fig = create_weekly_quantity_processed_figure(
        df_recovered, df_eliminated, date_interval
    )

    elements = [
        html.H4(
            f"Quantité de déchets dangereux tracés et traités par semaine {departement_filter_str}"
        ),
        dcc.Graph(figure=fig),
    ]
    return elements


def create_input_output_elements(
    departement_filter: str, waste_codes_filter: list[str]
):
    geographical_data = get_departement_geographical_data()
    bs_data = ALL_BORDEREAUX_DATA

    departement_filter_str = ""

    bs_data_filtered = bs_data
    if (departement_filter is not None) and (departement_filter != "all"):
        departement_filter_str = geographical_data.loc[
            geographical_data["code_departement"] == departement_filter,
            "libelle",
        ].item()
        bs_data_processed_incoming_filtered = bs_data[
            (bs_data["destination_departement"] == departement_filter)
            & (bs_data["emitter_departement"] != departement_filter)
        ]
        bs_data_processed_outgoing_filtered = bs_data[
            (bs_data["emitter_departement"] == departement_filter)
            & (bs_data["destination_departement"] != departement_filter)
        ]
        bs_data_processed_locally_filtered = bs_data[
            (bs_data["destination_departement"] == departement_filter)
            & (bs_data["emitter_departement"] == departement_filter)
        ]
    else:
        return no_update

    waste_filter_formatted = format_filter(
        bs_data_filtered["waste_code"], waste_codes_filter
    )
    if waste_filter_formatted is not None:

        bs_data_processed_incoming_filtered = bs_data_processed_incoming_filtered[
            waste_filter_formatted
        ]
        bs_data_processed_outgoing_filtered = bs_data_processed_outgoing_filtered[
            waste_filter_formatted
        ]
        bs_data_processed_locally_filtered = bs_data_processed_locally_filtered[
            waste_filter_formatted
        ]

    bs_data_processed_incoming_quantity = bs_data_processed_incoming_filtered[
        "quantity"
    ].sum()
    bs_data_processed_outgoing_quantity = bs_data_processed_outgoing_filtered[
        "quantity"
    ].sum()
    bs_data_processed_locally_quantity = bs_data_processed_locally_filtered[
        "quantity"
    ].sum()

    elements = [
        add_callout(
            number=bs_data_processed_locally_quantity,
            text=f"tonnes de déchets dangereux tracés et traités - {departement_filter_str}",
        ),
        add_callout(
            number=bs_data_processed_incoming_quantity,
            text=f"tonnes de déchets entrantes - {departement_filter_str}",
        ),
        add_callout(
            number=bs_data_processed_outgoing_quantity,
            text=f"tonnes de déchets sortantes - {departement_filter_str}",
        ),
    ]

    return elements
