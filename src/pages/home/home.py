"""This module is where the home page is registered and its initial layout rendered.
"""
from dash import dcc, html, register_page

from src.pages.home.home_layout_factory import get_header_elements
from src.pages.home.home_layouts import layout_2022

register_page(
    __name__,
    path="/",
    description="Page d'accueil des statistiques publiques de la plateforme Trackdéchets.",
    name="Accueil - Statistiques Publiques de Trackdéchets",
)


def layout() -> html.Div:
    """
    Creates initial layout for the home page. Currently the initial layout displays 2022 data.

    Returns
    -------
    A Dash Div with the id 'main-container'.
    """

    elements = [
        get_header_elements(),
        dcc.Loading(
            html.Div(
                layout_2022,
                id="graph-container",
            ),
            style={"position": "absolute", "top": "25px"},
            color="rgb(0, 0, 145)",
            type="circle",
        ),
    ]

    return html.Div(elements, id="main-container")
