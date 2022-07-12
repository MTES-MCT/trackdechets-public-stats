import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html


def add_figure(fig: go.Figure, fig_id: str) -> dbc.Row:
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

    row = dbc.Row(
        [
            dbc.Col(
                [
                    html.Div(
                        [dcc.Graph(id=fig_id, figure=fig, config={"locale": "fr"})],
                        className="fr-callout",
                    )
                ],
                width=12,
            )
        ]
    )
    return row


def format_number(input_number: float) -> str:
    """Format number, rounding it and adding spaces every three digits."""
    return f"{input_number:,.0f}".replace(",", " ")


def add_callout(
    text: str, width: int, sm_width: int = 0, number: int = None
) -> dbc.Col:
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
    small_width = width * 2 if sm_width == 0 else sm_width
    if number:
        # Below 1M
        if number < 1000000:
            number_class = "callout-number"
        # Above 10M
        elif number >= 10000000:
            number_class = "callout-number smaller-number"
        # From 1M to 10M-1
        # don't change initial value

    col = dbc.Col(
        html.Div(
            [
                html.P(format_number(number), className=number_class)
                if number
                else None,
                dcc.Markdown(text, className=text_class),
            ],
            className="fr-callout",
        ),
        width=small_width,
        lg=width,
        class_name="flex",
    )

    return col
