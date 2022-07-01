import dash_bootstrap_components as dbc
import plotly.express as px
from dash import html


from app.data.internal import (
    get_recent_bsdd_created_week,
    get_recent_bsdd_received,
    get_recent_bsdd_sent,
)
from app.layout.utils import add_figure


#################################################################################
#
#                   Internal stats figures and container
#
##################################################################################

# Created BSDD
internal_bsdd_created_week = px.line(
    get_recent_bsdd_created_week(),
    x="createdAt",
    y="count",
    text="count",
    title="BSDD créés par semaine",
    labels={
        "count": "BSDD créés",
        "createdAt": "Semaine de création",
    },
    markers=True,
)
internal_bsdd_created_week.update_traces(textposition="bottom right")

# Sent BSDD
internal_bsdd_sent_week = px.line(
    get_recent_bsdd_sent(),
    x="sentAt",
    y="count",
    text="count",
    title="BSDD enlevés par semaine",
    labels={
        "count": "BSDD enlevés",
        "sentAt": "Semaine d'enlèvement",
    },
    markers=True,
)
internal_bsdd_sent_week.update_traces(textposition="bottom right")

# Received BSDD
internal_bsdd_received_week = px.line(
    get_recent_bsdd_received(),
    x="receivedAt",
    y="count",
    text="count",
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
            [add_figure(internal_bsdd_sent_week, "internal_bsdd_sent_week")], width=10
        )
    ),
    dbc.Row(
        dbc.Col(
            [add_figure(internal_bsdd_received_week, "internal_bsdd_received_week")],
            width=10,
        )
    ),
]
