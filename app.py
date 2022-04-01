"""
Dashboard application to publish statistics about Trackdéchets (https://trackdechets.beta.gouv.fr)
"""

import dash_bootstrap_components.themes as dbc_themes
from dotenv import load_dotenv
import dash

# Load the environment variables in .env file, or from the host OS if no .env file
load_dotenv()

external_scripts = ["https://cdn.plot.ly/plotly-locale-fr-latest.js"]

# Use [dbc.themes.BOOTSTRAP] to import the full Bootstrap CSS
app = dash.Dash(
    "trackdechets-public-stats",
    title="Trackdéchets : statistiques et impact",
    external_stylesheets=[dbc_themes.GRID],
    external_scripts=external_scripts,
)

