"""This module is where the home page is registered and its initial layout rendered.
"""
from datetime import datetime
from dash import html, register_page, dcc

# This is needed so that dash properly registers callbacks
from src.pages.home.home_callbacks import *
from src.pages.home.home_layouts import layout_2022
from src.pages.home.home_layout_factory import get_header_elements, get_navbar_elements

register_page(
    __name__,
    path="/",
    description="Page d'accueil des statistiques publiques de la plateforme Trackdéchets.",
)


def layout() -> html.Div:
    """
    Creates initial layout. Currently the initial layout displays 2022 data.

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
