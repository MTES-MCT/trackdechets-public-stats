"""This module contains the callbacks for the home page.
"""

from dash import ALL, Input, Output, callback, ctx, html

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
def change_layout_for_year(n_clicks) -> tuple[list,html.Ul]:
    """This callback is triggered when the user clicks on the year selection menu.
    It updates the part of the layout containing all the graphs to display the data
    of the selected year.
    Also updates the year selection menu to change to 'selected' state the clicked button.

    Parameters
    ----------
    n_clicks: int
        The number of clicks on the menu links.

    Returns
    -------
    tuple
        The first elements is the layout as a list of dash elements
        ready to be inserted in the Div with id 'graph-container'.
        The second element is the updated navbar elements.
    """

    if all(e is None for e in n_clicks):
        year = 2022
    else:
        button_clicked = ctx.triggered_id
        year = button_clicked["index"]

    print(f"getting data for year {year}")

    return layouts[year], get_navbar_elements([2022, 2023], year)
