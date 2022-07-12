from os import getenv
from flask_caching import Cache

from app.app import dash_app


# Flask cache https://dash.plotly.com/performance
# timeout in seconds
appcache = Cache(
    dash_app.server, config={"CACHE_TYPE": "filesystem", "CACHE_DIR": "./cache"}
)
cache_timeout = int(getenv("CACHE_TIMEOUT_S"))
