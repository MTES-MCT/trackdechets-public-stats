from os import getenv

from src.app import app

# To use `gunicorn run:server` (prod)
server = app.server

# To use `python index.py` (dev)
if __name__ == "__main__":
    port = getenv("PORT", "8050")

    # Scalingo requires 0.0.0.0 as host, instead of the default 127.0.0.1
    app.run_server(
        debug=bool(getenv("DEVELOPMENT", "True")), host="0.0.0.0", port=int(port)
    )
