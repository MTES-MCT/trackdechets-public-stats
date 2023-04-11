"""
Dash app configuration
"""
from dash import html, page_container
from dash_extensions.enrich import DashProxy, html

external_scripts = ["https://cdn.plot.ly/plotly-locale-fr-latest.js"]
extra_config = {"locale": "fr"}

app = DashProxy(
    __name__,
    title="Trackdéchets : statistiques et impact",
    use_pages=True,
    external_scripts=external_scripts,
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "theme-color", "content": "#000091"}],
    update_title=None,
    assets_ignore = r"dsfr\.module\.min\.js|dsfr\.nomodule\.min\.js"

)


app.layout = html.Div(
    [
        page_container,
        html.Script(type="module", src=app.get_relative_path("/assets/dsfr.module.min.js")),
        html.Script(type="text/javascript",src=app.get_relative_path("/assets/dsfr.module.min.js"))
    ]
)
# Add the @lang attribute to the root <html>
app.index_string = app.index_string.replace("<html>", '<html lang="fr">')
