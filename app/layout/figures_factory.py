from datetime import timedelta
from typing import Optional

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from app.layout.utils import format_number

from app.layout.utils import format_number


def create_weekly_bs_created_figure(
    bs_data: pd.DataFrame,
) -> go.Figure:
    """Create the figure showing number of weekly created BSx"""

    text_positions = [
        "top center" if i % 2 else "bottom center" for i in range(bs_data.shape[0])
    ]

    texts = [
        f"Semaine du {e[0]-timedelta(days=6):%d/%m} au {e[0]:%d/%m}<br><b>{format_number(e[1])}</b> créations"
        for e in bs_data.itertuples(index=False)
    ]

    fig = go.Figure(
        [
            go.Scatter(
                x=bs_data["createdAt"],
                y=bs_data["id"],
                text=bs_data["id"],
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
        margin=dict(r=0, l=50),
    )
    fig.update_xaxes(tick0="2022-01-03")

    return fig


def create_weekly_quantity_processed_figure(
    bs_recovered_data: pd.DataFrame,
    bs_destroyed_data: pd.DataFrame,
    bs_other_data: Optional[pd.DataFrame],
) -> go.Figure:

    data_conf = [
        {
            "data": bs_recovered_data,
            "name": "Déchets valorisés",
            "text": "Semaine du {0:%d/%m} au {1:%d/%m}<br><b>{2}</b> tonnes de déchets valorisées",
            "color": "#66673D",
        },
        {
            "data": bs_destroyed_data,
            "name": "Déchets éliminés",
            "text": "Semaine du {0:%d/%m} au {1:%d/%m}<br><b>{2}</b> tonnes de déchets éliminées",
            "color": "#5E2A2B",
        },
    ]
    if bs_other_data is not None:
        data_conf.append(
            {
                "data": bs_other_data,
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
                x=data["processedAt"],
                y=data["weightValue"],
                name=conf["name"],
                hovertext=[
                    conf["text"].format(
                        e[0] - timedelta(days=6),
                        e.processedAt,
                        format_number(e.weightValue),
                    )
                    for e in bs_recovered_data.itertuples(index=False)
                ],
                hoverinfo="text",
                text=bs_recovered_data["weightValue"].apply(format_number),
                marker_color=conf["color"],
            )
        )

    fig = go.Figure(data=traces)

    fig.update_layout(
        xaxis_title="Semaine de création",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title="Type de traitement :",
        ),
        margin=dict(r=0, l=70),
        barmode="stack",
        yaxis_title="Quantité (en tonnes)",
    )

    return fig
