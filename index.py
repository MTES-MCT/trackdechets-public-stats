from os import getenv
from datetime import datetime, timedelta

from dateutil.tz import UTC
from dash import html, dcc
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
import pandas as pd
import sqlalchemy
import dash_bootstrap_components as dbc
from flask_caching import Cache
from dotenv import load_dotenv
import dash

from app import app

server = app.server

# Override the 'none' template
pio.templates["gouv"] = go.layout.Template(
    layout=dict(
        font=dict(family="Marianne"),
        title=dict(
            font=dict(
                color='black',
                size=22,
                family='Marianne-Bold'
            ),
            x=0.01
        ),
        paper_bgcolor='rgb(238, 238, 238)',
        colorway=['#2F4077', '#a94645', '#8D533E', '#417DC4'],
        yaxis=dict(
            tickformat=',0f',
            separatethousands=True,
        )
    ),
)

pio.templates.default = "none+gouv"