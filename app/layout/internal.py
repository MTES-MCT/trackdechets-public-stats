from typing import List

import dash_bootstrap_components as dbc
import plotly.express as px
from app.data.data_extract import get_bsd_data
from app.data.internal import (
    get_bsd_created,
    get_recent_bsdd_received,
    get_recent_bsdd_sent,
)
from app.layout.utils import add_figure
from dash import html




def get_internal_stats_container() -> List[dbc.Row]:
    """Create all figures needed for the internal stats page
    and returns an Dash HTML layout ready to be displayed.
    """
    bsd_data_df = get_bsd_data(include_drafts=True)

    bsd_created_weekly_df = get_bsd_created(bsd_data_df)

    # Created BSDD
    internal_bsdd_created_week = px.line(
        bsd_created_weekly_df,
        x="createdAt",
        y="id",
        text="id",
        title="BSDD créés par semaine",
        labels={
            "count": "BSDD créés",
            "createdAt": "Semaine de création",
        },
        markers=True,
    )
    internal_bsdd_created_week.update_traces(textposition="bottom right")

    recent_bsdd_sent_df = get_recent_bsdd_sent(bsd_data_df)
    # Sent BSDD
    internal_bsdd_sent_week = px.line(
        recent_bsdd_sent_df,
        x="sentAt",
        y="id",
        text="id",
        title="BSDD enlevés par semaine",
        labels={
            "count": "BSDD enlevés",
            "sentAt": "Semaine d'enlèvement",
        },
        markers=True,
    )
    internal_bsdd_sent_week.update_traces(textposition="bottom right")

    bsd_received_week = get_recent_bsdd_received(bsd_data_df)
    # Received BSDD
    internal_bsdd_received_week = px.line(
        bsd_received_week,
        x="receivedAt",
        y="id",
        text="id",
        title="BSDD réceptionnés par semaine",
        labels={
            "count": "BSDD réceptionnés",
            "receivedAt": "Semaine de réception",
        },
        markers=True,
    )
    internal_bsdd_received_week.update_traces(textposition="bottom right")

    internal_stats_container = [
        dbc.Row(
            dbc.Col(
                [
                    html.H1("Statistiques de montée en charge de Trackdéchets"),
                    html.H2("Bordereaux de suivi de déchets dangereux (BSDD)"),
                ]
            )
        ),
        dbc.Row(
            dbc.Col(
                [add_figure(internal_bsdd_created_week, "internal_bsdd_created_week")],
                width=10,
            )
        ),
        dbc.Row(
            dbc.Col(
                [add_figure(internal_bsdd_sent_week, "internal_bsdd_sent_week")],
                width=10,
            )
        ),
        dbc.Row(
            dbc.Col(
                [
                    add_figure(
                        internal_bsdd_received_week, "internal_bsdd_received_week"
                    )
                ],
                width=10,
            )
        ),
    ]

    return internal_stats_container
