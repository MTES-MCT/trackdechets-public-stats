"""This module contains the callbacks for the home page.
"""

from dash import ALL, Input, Output, callback, ctx, html, MATCH, State

from src.pages.home.home_layouts import layouts
from src.pages.home.home_layout_factory import get_navbar_elements
from src.pages.utils import format_number


@callback(
    output=[
        Output("graph-container", "children"),
        Output("header-navigation", "children"),
    ],
    inputs=[Input({"type": "year-selector", "index": ALL}, "n_clicks")],
    prevent_initial_call=True,
)
def change_layout_for_year(n_clicks) -> tuple[list, html.Ul]:
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


@callback(
    output=Output({"type": "counts-figure", "index": MATCH, "year": MATCH}, "figure"),
    inputs=[
        Input({"type": "counts-figure", "index": MATCH, "year": MATCH}, "relayoutData"),
        Input({"type": "counts-figure", "index": MATCH, "year": MATCH}, "restyleData"),
    ],
    state=[
        State({"type": "counts-figure", "index": MATCH, "year": MATCH}, "figure"),
    ],
    prevent_initial_call=True,
)
def relayout_figures_to_toggle_texts(relayout_data, restyle_data, figure):
    """This callback is triggered when the user zoom on a figure or disable a trace visibility.
    It updates the traces to toggle the text visibility depending of if it overlaps when another text.

    Parameters
    ----------
    relayout_data: dict
        Relayout event with associated data. Relayout event is triggered on zoom or drag.
    restyle_data: dict
        Restyle event with associated data. Restyle event is triggered when a trace is toggled on/off on legend click.
    figure :dict
        Figure data.
    Returns
    -------
    dict
        Updated figure data.
    """

    traces = figure["data"]

    if "yaxis.range[1]" not in relayout_data.keys():
        div_value = 0
        for trace in traces:
            if ("visible" in trace.keys()) and (trace["visible"] is not True):
                continue
            max_ = max(trace["y"])
            if max_ > div_value:
                div_value = max_
    else:
        div_value = relayout_data["yaxis.range[1]"] - relayout_data["yaxis.range[0]"]

    div_value = max(0.01, div_value)

    texts_positionned = []
    new_traces = []
    for trace in traces:
        if not ("visible" in trace.keys()) or (trace["visible"] is True):

            last_value = trace["y"][-1]
            overlaps = any(
                abs(last_value - e) / div_value < 0.04 for e in texts_positionned
            )
            if not overlaps or len(texts_positionned) == 0:
                trace["text"] = trace["text"][:-1] + [format_number(last_value)]
                texts_positionned.append(last_value)
            else:
                trace["text"] = [""] * len(trace["x"])
        new_traces.append(trace)

    figure["data"] = new_traces
    return figure
