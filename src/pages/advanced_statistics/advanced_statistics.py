"""This module is where the advanced statistics page is registered and its initial layout rendered.
"""

from dash import dcc, html, register_page

from src.pages.advanced_statistics.advanced_statistics_layout_factory import \
    create_filters_selects_elements

register_page(
    __name__,
    path="/statistiques-avancees",
    description="Mode avancée de consultation des statistiques publiques de la plateforme Trackdéchets.",
    name="Mode avancé - Statistiques Publiques de Trackdéchets",
)


def layout() -> html.Div:
    """
    Creates initial layout.

    Returns
    -------
    A Dash Div with the id 'main-container'.
    """

    elements = [
        create_filters_selects_elements(),
        html.Div(
            dcc.Loading(
                [
                    html.Div(
                        className="fr-callout", id="total-processed-figures-container"
                    ),
                    html.Div(id="waste-processed-fig", className="fr-callout"),
                ],
                style={"position": "absolute", "top": "25px"},
                color="rgb(0, 0, 145)",
                type="circle",
            ),
        ),
    ]

    return html.Div(
        html.Div(html.Div(elements, className="fr-col"), className="fr-grid-row"),
        id="main-container",
        className="fr-container",
    )
