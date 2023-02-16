"""
Dash app configuration
"""
from dash import Dash, html, page_container

external_scripts = ["https://cdn.plot.ly/plotly-locale-fr-latest.js"]
extra_config = {"locale": "fr"}

app = Dash(
    __name__,
    title="Trackdéchets : statistiques et impact",
    external_scripts=external_scripts,
    use_pages=True,
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "theme-color", "content": "#000091"}],
    update_title=None,
)


app.layout = html.Div(
    [
        page_container,
    ]
)
# Add the @lang attribute to the root <html>
app.index_string = app.index_string.replace("<html>", '<html lang="fr">')
