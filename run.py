from os import getenv

from app.app import dash_app

# To use `gunicorn run:server` (prod)
server = dash_app.server

# To use `python index.py` (dev)
if __name__ == "__main__":
    port = getenv("PORT", "8050")

    # Scalingo requires 0.0.0.0 as host, instead of the default 127.0.0.1
    dash_app.run_server(
        debug=bool(getenv("DEVELOPMENT", True)), host="0.0.0.0", port=int(port)
    )
