from app.layout.public import get_public_stats_container
from dash import html
import dash_bootstrap_components as dbc

# Router
# @callback(Output("layout-container", "children"), [Input("url", "pathname")])
# def display_page(pathname):
#     if pathname == "/":
#         return public_stats_container
#     elif pathname == "/internal-stats":
#         return internal_stats_container
#     else:
#         return 'Page inconnue : "' + pathname + '"'


def serve_layout() -> html:
    print("layout served")
    layout = html.Main(
        children=[
            # dcc.Location(id="url", refresh=False),
            dbc.Container(
                fluid=True, id="layout-container", children=get_public_stats_container()
            ),
        ]
    )

    return layout
