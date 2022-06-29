import dash
from flask_caching import Cache

# Flask cache https://dash.plotly.com/performance
# timeout in seconds
appcache = Cache(config={"CACHE_TYPE": "filesystem", "CACHE_DIR": "./cache"})
cache_timeout = int(1)
