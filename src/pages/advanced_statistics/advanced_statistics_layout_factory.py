from datetime import datetime
from zoneinfo import ZoneInfo

from dash import dcc, html
from dash.development.base_component import Component
import polars as pl
from feffery_antd_components.AntdTree import AntdTree

from src.data.data_extract import (
    get_departement_geographical_data,
    get_waste_code_hierarchical_nomenclature,
)
from src.data.data_processing import (
    get_recovered_and_eliminated_quantity_processed_by_week_series,
    get_weekly_waste_quantity_processed_by_operation_code_df,
)
from src.data.datasets import ALL_BORDEREAUX_DATA, DEPARTEMENTS_GEOGRAPHICAL_DATA
from src.pages.advanced_statistics.utils import format_filter
from src.pages.figures_factory import create_weekly_quantity_processed_figure
from src.pages.utils import add_callout


def create_filters_selects_elements() -> html.Div:
    """
    Returns a `html.Div` object containing the filters for selecting departments and waste codes.

    Returns
    -------
    html.Div
        A `html.Div` object containing the filters.

    """

    geographical_data = DEPARTEMENTS_GEOGRAPHICAL_DATA
    waste_nomenclature = get_waste_code_hierarchical_nomenclature()

    geographical_data = geographical_data.to_dict(as_series=False)
    options = [
        {"value": a, "label": b}
        for a, b in zip(
            geographical_data["code_departement"], geographical_data["libelle"]
        )
    ]

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
    departement_filter: str, waste_codes_filter: dict[str, list[str]]
) -> list[Component]:
    """
    Create a plot of the quantity of hazardous waste processed and tracked by week. The data is, if needed, filtered by departement
    and waste codes.

    Parameters:
    -----------
    departement_filter : str
        The code of the departement to filter the data by. If "all" is passed, all departements will be included in the
        plot.
    waste_codes_filter : dict with "checked" and "half checked" keys
        The dictionary that contains the waste codes checked or half-checked on UI that will be used for filtering.

    Returns:
    --------
    list
        A list of dash elements that are ready to be rendered.

    Example:
    --------
    >>> create_filtered_waste_processed_figure("75", {"checked": ["01 01","01 01 01*",,"19", "19 01", "19 01 01"], "half_checked": ["01"]})
    [html.H4("Quantité de déchets dangereux tracés et traités par semaine - Paris"),
     dcc.Graph(figure=...)]

    """
    geographical_data = DEPARTEMENTS_GEOGRAPHICAL_DATA
    bs_data = ALL_BORDEREAUX_DATA

    departement_filter_str = ""

    bs_data_filtered = bs_data
    if (departement_filter is not None) and (departement_filter != "all"):
        departement_filter_str = (
            "- "
            + geographical_data.filter(
                pl.col("code_departement") == departement_filter
            )["libelle"].item()
        )
        bs_data_filtered = bs_data.filter(
            pl.col("destination_departement") == departement_filter
        )

    waste_filter_formatted = format_filter(pl.col("waste_code"), waste_codes_filter)
    if waste_filter_formatted is not None:

        bs_data_filtered = bs_data_filtered.filter(waste_filter_formatted)

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
        bs_data_filtered_grouped
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
    departement_filter: str, waste_codes_filter: dict[str, list[str]]
) -> list[Component]:
    """
    Create input/output elements for a Dash application.

    Parameters
    ----------
    departement_filter : str
        The filter to apply on the departement data. If set to 'all', no filter is applied.
    waste_codes_filter : list[str]
        The list of waste codes to filter the bordereaux data by.

    Returns
    -------
    list
        A list of Dash elements, each containing the quantity of incoming, outgoing, or locally processed
        dangerous waste in a specific departement.
        If no departemenent filter is provided (departement_filter is None or "all"), then nothing is returned.

    """
    geographical_data = get_departement_geographical_data()
    bs_data = ALL_BORDEREAUX_DATA

    departement_filter_str = ""

    if (departement_filter is not None) and (departement_filter != "all"):
        departement_filter_str = geographical_data.filter(
            pl.col("code_departement") == departement_filter
        )["libelle"].item()

        bs_data_processed_incoming_filtered = bs_data.filter(
            (pl.col("destination_departement") == departement_filter)
            & (pl.col("emitter_departement") != departement_filter)
        )
        bs_data_processed_outgoing_filtered = bs_data.filter(
            (pl.col("emitter_departement") == departement_filter)
            & (pl.col("destination_departement") != departement_filter)
        )
        bs_data_processed_locally_filtered = bs_data.filter(
            (pl.col("destination_departement") == departement_filter)
            & (pl.col("emitter_departement") == departement_filter)
        )
        elements = [
            html.H4(f"Flux de déchet du département - {departement_filter_str}"),
        ]
    else:
        return [
            html.H4("Flux de déchet du département"),
            html.Div(
                "Veuillez sélectionner un département pour afficher les données",
                id="departement-figure-no-data",
            ),
        ]

    waste_filter_formatted = format_filter(pl.col("waste_code"), waste_codes_filter)
    if waste_filter_formatted is not None:

        bs_data_processed_incoming_filtered = (
            bs_data_processed_incoming_filtered.filter(waste_filter_formatted)
        )
        bs_data_processed_outgoing_filtered = (
            bs_data_processed_outgoing_filtered.filter(waste_filter_formatted)
        )
        bs_data_processed_locally_filtered = bs_data_processed_locally_filtered.filter(
            waste_filter_formatted
        )

    bs_data_processed_incoming_quantity = (
        bs_data_processed_incoming_filtered.select("quantity").sum().item()
    )
    bs_data_processed_outgoing_quantity = (
        bs_data_processed_outgoing_filtered.select("quantity").sum().item()
    )
    bs_data_processed_locally_quantity = (
        bs_data_processed_locally_filtered.select("quantity").sum().item()
    )

    elements.extend(
        [
            html.Div(
                [
                    add_callout(
                        number=bs_data_processed_locally_quantity,
                        text="tonnes de déchets dangereux tracés et traités à l’intérieur du département",
                    ),
                    add_callout(
                        number=bs_data_processed_incoming_quantity,
                        text="tonnes de déchets entrantes traités à l’intérieur du département",
                    ),
                    add_callout(
                        number=bs_data_processed_outgoing_quantity,
                        text="tonnes de déchets sortantes traités à l’extérieur du département",
                    ),
                ],
                id="total-processed-figures",
                className="row",
            ),
        ]
    )

    return elements  # type: ignore
