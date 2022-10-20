from datetime import timedelta
from typing import Optional

import pandas as pd
import plotly.graph_objects as go

from app.layout.utils import format_number


def create_weekly_created_figure(
    data: pd.DataFrame,
) -> go.Figure:
    """Creates the figure showing number of weekly created Bsx, companies, users...

    Parameters
    ----------
    data: DataFrame
        DataFrame containing the data to plot. Must have 'id' and 'at' columns.

    Returns
    -------
    Plotly Figure Object
        Figure object ready to be plotted.
    """

    text_positions = [
        "top center" if i % 2 else "bottom center" for i in range(data.shape[0])
    ]

    texts = [
        f"Semaine du {e[0]-timedelta(days=6):%d/%m} au {e[0]:%d/%m}<br><b>{format_number(e[1])}</b> créations"
        for e in data.itertuples(index=False)
    ]

    fig = go.Figure(
        [
            go.Scatter(
                x=data["at"],
                y=data["id"],
                text=data["id"],
                mode="lines+markers+text",
                hovertext=texts,
                hoverinfo="text",
                textposition=text_positions,
            )
        ]
    )

    fig.update_layout(
        xaxis_title="Semaine de création",
        showlegend=False,
        paper_bgcolor="#fff",
        margin=dict(t=20, r=0, l=50),
    )
    fig.update_xaxes(tick0="2022-01-03")

    return fig


def create_weekly_counts_scatter_figure(
    bs_created_data: pd.DataFrame,
    bs_sent_data: pd.DataFrame,
    bs_processed_data: pd.DataFrame,
) -> go.Figure:
    """Creates a scatter figure showing the weekly number of 'bordereaux' by status (created, sent..)

    Parameters
    ----------
    bs_created_data: DataFrame
        DataFrame containing the count of 'bordereaux' created. Must have 'id' and 'at' columns.
    bs_sent_data: DataFrame
        DataFrame containing the count of 'bordereaux' sent. Must have 'id' and 'at' columns.
    bs_processed_data: DataFrame
        DataFrame containing the count of 'bordereaux' processed. Must have 'id' and 'at' columns.

    Returns
    -------
    Plotly Figure Object
        Figure object ready to be plotted.
    """

    plot_configs = [
        {
            "data": bs_created_data,
            "name": "Bordereaux créés",
            "suffix": "créations",
        },
        {
            "data": bs_sent_data,
            "name": "Bordereaux envoyés",
            "suffix": "envois",
        },
        {
            "data": bs_processed_data,
            "name": "Bordereaux traités",
            "suffix": "traitements",
        },
    ]

    scatter_list = []

    for config in plot_configs:

        data = config["data"]
        name = config["name"]
        suffix = config["suffix"]

        # Creates a list of text to only show value on last point of the line
        texts = [""] * (len(data) - 1) + [format_number(data["id"].iloc[-1])]

        hover_texts = [
            f"Semaine du {e[0]-timedelta(days=6):%d/%m} au {e[0]:%d/%m}<br><b>{format_number(e[1])}</b> {suffix}"
            for e in data.itertuples(index=False)
        ]

        scatter_list.append(
            go.Scatter(
                x=data["at"],
                y=data["id"],
                mode="lines+text",
                name=name,
                text=texts,
                textfont_size=15,
                textposition="top right",
                hovertext=hover_texts,
                hoverinfo="text",
                line_shape="spline",
                line_smoothing=0.3,
                line_width=3,
            )
        )

    fig = go.Figure(scatter_list)

    fig.update_layout(
        paper_bgcolor="#fff",
        margin=dict(t=5, r=70, l=5),
        legend=dict(orientation="h", y=1, font_size=13, itemwidth=40),
    )
    fig.update_xaxes(tick0="2022-01-03")
    fig.update_yaxes(side="right")

    return fig


def create_weekly_quantity_processed_figure(
    bs_recovered_data: pd.Series,
    bs_destroyed_data: pd.Series,
    bs_other_data: Optional[pd.Series],
) -> go.Figure:
    """Creates the figure showing the weekly waste quantity processed by type of process (destroyed or recovered).

    Parameters
    ----------
    bs_recovered_data: DataFrame
        DataFrame containing the quantity of recovered waste aggregated by week.
    bs_destroyed_data: DataFrame
        DataFrame containing the quantity of destroyed waste aggregated by week.
    bs_other_data: DataFrame
        Optional. DataFrame containing the quantity of waste that is neither recovered or destroyed aggregated by week.

    Returns
    -------
    Plotly Figure Object
        Figure object ready to be plotted.
    """

    data_conf = [
        {
            "data": bs_recovered_data.reset_index(),
            "name": "Déchets valorisés",
            "text": "Semaine du {0:%d/%m} au {1:%d/%m}<br><b>{2}</b> tonnes de déchets valorisées",
            "color": "#66673D",
        },
        {
            "data": bs_destroyed_data.reset_index(),
            "name": "Déchets éliminés",
            "text": "Semaine du {0:%d/%m} au {1:%d/%m}<br><b>{2}</b> tonnes de déchets éliminées",
            "color": "#5E2A2B",
        },
    ]
    if bs_other_data is not None:
        data_conf.append(
            {
                "data": bs_other_data.reset_index(),
                "name": "Autre",
                "text": "Semaine du {0:%d/%m} au {1:%d/%m}<br><b>{2}</b> tonnes de déchets",
                "color": "#6A6A6A",
            }
        )

    traces = []
    for conf in data_conf:

        data = conf["data"]
        traces.append(
            go.Bar(
                x=data["processed_at"],
                y=data["quantity"],
                name=conf["name"],
                hovertext=[
                    conf["text"].format(
                        e[0] - timedelta(days=6),
                        e.processed_at,
                        format_number(e.quantity),
                    )
                    for e in data.itertuples(index=False)
                ],
                hoverinfo="text",
                text=data["quantity"].apply(format_number),
                marker_color=conf["color"],
            )
        )

    fig = go.Figure(data=traces)

    max_value = sum([conf["data"]["quantity"].max() for conf in data_conf])
    fig.update_layout(
        xaxis_title="Semaine de traitement",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title="Type de traitement :",
        ),
        margin=dict(t=30, r=70, l=0),
        barmode="stack",
        yaxis_title="Quantité (en tonnes)",
        yaxis_range=[0, max_value * 1.1],
    )
    fig.update_yaxes(side="right")

    return fig
