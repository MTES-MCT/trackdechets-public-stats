"""This module is where the advanced statistics page is registered and its initial layout rendered.
"""

from dash import dcc, html, register_page

from src.pages.advanced_statistics.advanced_statistics_layout_factory import (
    create_selects,
)

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

    elements = [create_selects()]

    return html.Div(elements, id="main-container")
