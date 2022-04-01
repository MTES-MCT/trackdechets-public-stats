"""
Dash app configuration
"""
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
import dash

# Load the environment variables in .env file, or from the host OS if no .env file
load_dotenv()

external_scripts = ["https://cdn.plot.ly/plotly-locale-fr-latest.js"]
extra_config = {"locale": "fr"}

# Use [dbc.themes.BOOTSTRAP] to import the full Bootstrap CSS
app = dash.Dash(
    __name__,
    title="Trackdéchets : statistiques et impact",
    external_stylesheets=[dbc.themes.GRID],
    external_scripts=external_scripts,
)

# Add the @lang attribute to the root <html>
app.index_string = app.index_string.replace('<html>', '<html lang="fr">')
# print(app.index_string)
