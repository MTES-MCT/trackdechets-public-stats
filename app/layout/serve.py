import os
from typing import List

import dash_bootstrap_components as dbc
from app.layout.internal import get_internal_stats_container
from app.layout.public import get_public_stats_container
from dash import Input, Output, callback, dcc, html

PUBLIC_STATS_CONTAINER = get_public_stats_container()
INTERNAL_STATS_CONTAINER = get_internal_stats_container()
# Router
@callback(Output("layout-container", "children"), [Input("url", "pathname")])
def display_page(pathname: str) -> List[dbc.Row]:
    """Returns either public stats or internal stats container
    dependeing on request path.

    Parameters
    -----------
    pathname: str
        path requested

    Returns
    --------
    A Dash HTML layout that depends on the path and that is ready to be displayed.
    """
    if pathname == "/":
        return PUBLIC_STATS_CONTAINER
    elif pathname == "/internal-stats":
        return INTERNAL_STATS_CONTAINER
    else:
        return 'Page inconnue : "' + pathname + '"'


def serve_layout() -> html.Main:
    """Returns initial layout that will be updated depending on request path using function
    `display_page`.
    """

    layout = html.Main(
        children=[
            dcc.Location(id="url", refresh=False),
            dbc.Container(fluid=True, id="layout-container", children=[]),
        ]
    )
    print("layout served")
    return layout
