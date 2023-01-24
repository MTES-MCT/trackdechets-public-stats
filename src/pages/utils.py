import re

import plotly.graph_objects as go
from dash import dcc, html


def add_figure(
    fig: go.Figure, fig_id: str, figure_title: str, figure_subtitle: str = None
) -> html.Div:
    """
    Boilerplate for figure rows.

    Parameters
    -----------
    fig: Figure
        a plotly figure
    fig_id: str
        if of the figure in the resulting HTML

    Returns
    -------
    HTML Row to be added in a Dash layout
    """
    elements = [html.H4(children=[figure_title])]

    if figure_subtitle is not None:
        elements.append(html.Div(figure_subtitle, className="figure-subtitle fr-text"))

    elements.append(
        dcc.Graph(
            id=fig_id,
            figure=fig,
            config={
                "locale": "fr",
                "toImageButtonOptions": {
                    "format": "png",  # one of png, svg, jpeg, webp
                    "filename": "trackdechets",
                    "height": 1080,
                    "width": 1920,
                    "scale": 1,  # Multiply title/legend/axis/canvas sizes by this factor
                },
                "displaylogo": False,
            },
        )
    )

    row = html.Div(
        elements,
        className="fr-callout",
    )

    return row


def format_number(input_number: float, precision: int = 0) -> str:
    """Format a float to a string with thousands separated by space and rounding it at the given precision."""
    input_number = round(input_number, precision)
    return re.sub(r"\.0+", "", "{:,}".format(input_number).replace(",", " "))


def add_callout(text: str, number: int = None) -> html.Div:
    """
    Create a callout element with text and optional number.

    Parameters
    -----------
    text: str
        Text to add to the callout element.
    width: int
        Width of the callout, in number of columns.
    sm_width: int
        Use to specified the width of the callout element on small screens.
        Default value 0 will set the small_width to two times the width.
    number: Optional. Number to display in the callout element.

    Returns
    -------
    A Col instance representing the HTML callout element.
    """
    text_class = "number-text" if number else "fr-callout__text"
    number_class = "callout-number small-number"
    if number:
        # Below 1M
        if number < 1000000:
            number_class = "callout-number"
        # Above 10M
        elif number >= 10000000:
            number_class = "callout-number smaller-number"
        # From 1M to 10M-1
        # don't change initial value

    col = html.Div(
        [
            html.P(format_number(number), className=number_class) if number else None,
            dcc.Markdown(text, className=text_class),
        ],
        className="fr-callout",
    )

    return col


def break_long_line(line: str, max_line_length: int = 26, max_length: int = 60) -> str:
    """Format a string to add HTML line breaks (<br>) if it exceeds max_line_length."""
    length = 0

    # line = line[:max_length] + "..."
    new_pieces = []
    for piece in line.split(" "):
        length += len(piece)
        if length > max_line_length:
            piece = "<br>" + piece
            length = 0
        new_pieces.append(piece)

    return " ".join(new_pieces).replace(" <br>", "<br>")
