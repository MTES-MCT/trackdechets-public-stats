"""
Dashboard application to publish statistics about Trackdéchets (https://trackdechets.beta.gouv.fr)
"""
from os import getenv
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
import dash
import dashboard

# Load the environment variables in .env file, or from the host OS if no .env file
load_dotenv()

external_scripts = ["https://cdn.plot.ly/plotly-locale-fr-latest.js"]

# Use [dbc.themes.BOOTSTRAP] to import the full Bootstrap CSS
app = dash.Dash(
    "trackdechets-public-stats",
    title="Trackdéchets : statistiques et impact",
    external_stylesheets=[dbc.themes.GRID],
    external_scripts=external_scripts,
)
app.layout = dashboard.layout
server = app.server


if __name__ == "__main__":
    port = getenv("PORT", "8050")

    # Scalingo requires 0.0.0.0 as host, instead of the default 127.0.0.1
    app.run_server(debug=bool(getenv("DEVELOPMENT")), host="0.0.0.0", port=int(port))
