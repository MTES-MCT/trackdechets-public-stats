"""
Dash dash_app configuration
"""
import dash_bootstrap_components as dbc
import dash

from app.index import serve_layout
from os import getenv
from flask_caching import Cache

external_scripts = ["https://cdn.plot.ly/plotly-locale-fr-latest.js"]
extra_config = {"locale": "fr"}

# Use [dbc.themes.BOOTSTRAP] to import the full Bootstrap CSS
dash_app = dash.Dash(
    __name__,
    title="Trackdéchets : statistiques et impact",
    external_stylesheets=[dbc.themes.GRID],
    external_scripts=external_scripts,
)

appcache = Cache(
    dash_app.server, config={"CACHE_TYPE": "filesystem", "CACHE_DIR": "./cache"}
)
cache_timeout = int(1)

dash_app.layout = serve_layout
# Add the @lang attribute to the root <html>
dash_app.index_string = dash_app.index_string.replace("<html>", '<html lang="fr">')
# print(dash_app.index_string)
