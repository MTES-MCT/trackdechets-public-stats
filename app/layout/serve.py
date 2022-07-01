from app.layout.public import get_public_stats_container
from app.layout.internal import get_internal_stats_container
from dash import html, Input, Output, callback, dcc
import dash_bootstrap_components as dbc

# Router
@callback(Output("layout-container", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/":
        return get_public_stats_container()
    elif pathname == "/internal-stats":
        return get_internal_stats_container()
    else:
        return 'Page inconnue : "' + pathname + '"'


def serve_layout() -> html:

    layout = html.Main(
        children=[
            dcc.Location(id="url", refresh=False),
            dbc.Container(fluid=True, id="layout-container", children=[]),
        ]
    )
    print("layout served")
    return layout
