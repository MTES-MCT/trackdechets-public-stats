import datetime

import dash
from dash import dcc
from dash import html
import plotly.express as px
import plotly.io as pio
import pandas as pd
from sqlalchemy import create_engine
from os import getenv
import dash_bootstrap_components as dbc
from datetime import date

external_scripts = ['https://cdn.plot.ly/plotly-locale-fr-latest.js']
config = {'locale': 'fr'}
app = dash.Dash("trackdechets-public-stats", title='Trackdéchets : statistiques et impact',
                external_stylesheets=[dbc.themes.BOOTSTRAP], external_scripts=external_scripts)
pio.templates.default = "simple_white"

# postgresql://admin:admin@localhost:5432/ibnse
engine = create_engine(getenv('DATABASE_URL'))

df_bsdd = pd.read_sql_query(
    'SELECT id, status, "Form"."createdAt", "Form"."isDeleted", "Form"."processedAt", "Form"."quantityReceived" FROM "default$default"."Form" '
    'WHERE "Form"."createdAt" >= CAST((CAST(now() AS timestamp) + (INTERVAL \'-30 day\'))AS date) AND '
    '"Form"."isDeleted" = FALSE AND "Form"."status" <> \'DRAFT\'',
    con=engine)

#  2020-10-26 14:52:54.995 ===> 2020-10-26
for col in ['createdAt', 'processedAt']:
    df_bsdd[col] = df_bsdd[col].dt.date

bsdd = df_bsdd.count()[0]
fig = px.bar(df_bsdd.groupby(by='status').count().sort_values(['id'], ascending=True), x='id',
             title="Répartition des BSDD "
                   "par statut")
nb_sent = df_bsdd.query("status=='SENT'")
quantity_processed = df_bsdd[['processedAt', 'quantityReceived']].groupby(by='processedAt').sum()
quantity_processed_daily = px.bar(quantity_processed,
                                  y='quantityReceived',
                                  labels={'quantityReceived': 'Quantité traitée (tonnes)',
                                          'processedAt': 'Date du traitement'})

app.layout = html.Div(children=[
    dbc.Container(fluid=True, children=[
        dbc.Row(
            [
                html.P("L'application Trackdéchets est utilisée en France par des milliers de professionnels du "
                       "déchet pour déclarer les déchets produits, ainsi que les différentes manipulations, jusqu'au "
                       "traitement final."),
                html.P("Un borderau de suivi de déchet (BSD) est créé pour chaque conteneur (sac, baril, "
                       "bidon, etc.) ou groupement de conteneurs . De nombreuses informations telles que le type de "
                       "déchet, le poids, et les enteprises impliquées sont envoyées à Trackdéchets."),
                html.P("Aujourd'hui, l'utilisation de Trackdéchets est obligatoire pour les déchets dangereux (DD) et "
                       "les déchet d'amiante (DA).")
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id='example-graph',
                        figure=quantity_processed_daily,
                        config=config
                    ), width=6
                ),
                dbc.Col(
                    dcc.Graph(
                        id='example-graph2',
                        figure=fig,
                        config=config
                    ), width=6
                )
            ]
        )
    ]
                  )

])

if __name__ == '__main__':
    port = getenv('PORT', 8050)

    # Scalingo requires 0.0.0.0 as host, instead of the default 127.0.0.1
    app.run_server(debug=True, host='0.0.0.0', port=int(port))
