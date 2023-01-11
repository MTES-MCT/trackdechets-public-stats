from dash import ALL, Input, Output, callback, ctx, State

from src.pages.home.home_layouts import layouts
from src.pages.home.home_layout_factory import get_navbar_elements


@callback(
    output=[
        Output("graph-container", "children"),
        Output("header-navigation", "children"),
    ],
    inputs=[Input({"type": "year-selector", "index": ALL}, "n_clicks")],
    prevent_initial_call=True,
)
def change_layout_for_year(clicks):

    if all(e is None for e in clicks):
        year = 2022
    else:
        button_clicked = ctx.triggered_id
        year = button_clicked["index"]

    print(f"getting data for year {year}")

    return layouts[year], get_navbar_elements([2022, 2023], year)
