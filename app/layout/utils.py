import dash_bootstrap_components as dbc
from dash import html, dcc


def add_figure(fig, fig_id: str) -> dbc.Row:
    """
    Boilerplate for figure rows.
    :param fig: a plotly figure
    :param fig_id: if of the figure in the resulting HTML
    :return: HTML Row to be added in a Dash layout
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


def format_number(input_number) -> str:
    return "{:,.0f}".format(input_number).replace(",", " ")


def add_callout(text: str, width: int, sm_width: int = 0, number: int = None):
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
