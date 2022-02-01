# Trackdechets database connection string
export DATABASE_URL="postgresql://admin:admin@localhost:5432/database"

# Time in seconds during which database queries are cached server-side
# https://dash.plotly.com/performance
export CACHE_TIMEOUT_S=3600

# The period of time covered by the statistics, in days
export TIME_PERIOD_D=30

# The port the app should listen to
# defaults to 8050 in the app code
export PORT=8050