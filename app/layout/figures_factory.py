from datetime import timedelta

import pandas as pd
import plotly.graph_objects as go


def create_weekly_bs_created_figure(
    bsdd_data: pd.DataFrame,
    bsda_data: pd.DataFrame,
    bsff_data: pd.DataFrame,
    bsdasri_data: pd.DataFrame,
) -> go.Figure:
    """Create the figure showing number of weekly created BSx"""

    lines_def = [
        {"name": "BSDD", "data": bsdd_data},
        {"name": "BSDA", "data": bsda_data},
        {"name": "BSFF", "data": bsff_data},
        {"name": "BSDASRI", "data": bsdasri_data},
    ]
    lines = []

    for line_def in lines_def:
        data: pd.DataFrame = line_def["data"]

        text_positions = [
            "top center" if i % 2 else "bottom center" for i in range(data.shape[0])
        ]

        texts = [
            f"Semaine du {e[0]-timedelta(days=6):%d/%m} au {e[0]:%d/%m}<br><b>{e[1]}</b> créations"
            for e in data.itertuples(index=False)
        ]

        lines.append(
            go.Scatter(
                x=data["createdAt"],
                y=data["id"],
                text=data["id"],
                name=line_def["name"],
                mode="lines+markers+text",
                hovertext=texts,
                hoverinfo="text+name",
                textposition=text_positions,
            )
        )

    fig = go.Figure(lines)

    fig.update_layout(
        title="Bordereaux créées par semaine",
        xaxis_title="Semaine de création",
    )
    fig.update_xaxes(tick0="2022-01-03")

    return fig
