"""
Dash dash_app configuration
"""
import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.io as pio

from app.layout import cache
from app.layout.serve import serve_layout

external_scripts = ["https://cdn.plot.ly/plotly-locale-fr-latest.js"]
extra_config = {"locale": "fr"}

# Use [dbc.themes.BOOTSTRAP] to import the full Bootstrap CSS
dash_app = dash.Dash(
    __name__,
    title="Trackdéchets : statistiques et impact",
    external_stylesheets=[dbc.themes.GRID],
    external_scripts=external_scripts,
)

# Override the 'none' template
pio.templates["gouv"] = go.layout.Template(
    layout=dict(
        font=dict(family="Marianne"),
        title=dict(font=dict(color="black", size=22, family="Marianne-Bold"), x=0.01),
        paper_bgcolor="rgb(238, 238, 238)",
        colorway=["#2F4077", "#a94645", "#8D533E", "#417DC4"],
        yaxis=dict(
            tickformat=",0f",
            separatethousands=True,
        ),
    ),
)

pio.templates.default = "none+gouv"

# cache initialisation
cache.init_app(dash_app.server)

dash_app.layout = serve_layout()
# Add the @lang attribute to the root <html>
dash_app.index_string = dash_app.index_string.replace("<html>", '<html lang="fr">')
