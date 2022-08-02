"""
Dash dash_app configuration
"""
import dash
import dash_bootstrap_components as dbc

from app.layout.serve import serve_layout

external_scripts = ["https://cdn.plot.ly/plotly-locale-fr-latest.js"]
extra_config = {"locale": "fr"}

# Use [dbc.themes.BOOTSTRAP] to import the full Bootstrap CSS
dash_app = dash.Dash(
    __name__,
    title="Trackdéchets : statistiques et impact",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    external_scripts=external_scripts,
    assets_external_path="",
)

dash_app.layout = serve_layout()
# Add the @lang attribute to the root <html>
dash_app.index_string = dash_app.index_string.replace("<html>", '<html lang="fr">')
