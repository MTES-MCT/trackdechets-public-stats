import dash_bootstrap_components as dbc
from app.layout.public import get_public_stats_container
from dash import dcc, html

PUBLIC_STATS_CONTAINER = get_public_stats_container()


def serve_layout() -> html.Main:
    """Returns initial layout that will be updated depending on request path using function
    `display_page`.
    """

    layout = html.Main(
        children=[
            dcc.Location(id="url", refresh=False),
            dbc.Container(
                fluid=True, id="layout-container", children=PUBLIC_STATS_CONTAINER
            ),
        ]
    )
    print("layout served")
    return layout
