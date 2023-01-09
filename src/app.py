"""
Dash dash_app configuration
"""
from dash import Dash, html, dcc, page_container, page_registry


external_scripts = ["https://cdn.plot.ly/plotly-locale-fr-latest.js"]
extra_config = {"locale": "fr"}

app = Dash(
    __name__,
    title="Trackdéchets : statistiques et impact",
    external_scripts=external_scripts,
    use_pages=True,
)


app.layout = html.Div(
    [
        page_container,
    ]
)
# Add the @lang attribute to the root <html>
app.index_string = app.index_string.replace("<html>", '<html lang="fr">')
