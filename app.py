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
from datetime import datetime, timedelta

external_scripts = ['https://cdn.plot.ly/plotly-locale-fr-latest.js']
config = {'locale': 'fr'}
app = dash.Dash("trackdechets-public-stats", title='Trackdéchets : statistiques et impact',
                external_stylesheets=[dbc.themes.BOOTSTRAP], external_scripts=external_scripts)
pio.templates.default = "simple_white"

# postgresql://admin:admin@localhost:5432/ibnse
engine = create_engine(getenv('DATABASE_URL'))

df_bsdd = pd.read_sql_query(
    'SELECT id, status, cast("Form"."createdAt" as date), "Form"."isDeleted", cast("Form"."processedAt" as date), '
    '"Form"."quantityReceived" FROM "default$default"."Form" '
    'WHERE "Form"."isDeleted" = FALSE AND "Form"."status" <> \'DRAFT\'',
    con=engine)

#  2020-10-26 14:52:54.995 ===> 2020-10-26
# df_bsdd['createdAt'] = df_bsdd['createdAt'].dt.date
# df_bsdd['processedAt'] = df_bsdd['processedAt'].dt.date

date_n_days_ago = datetime.date(datetime.today() - timedelta(30))

df_bsdd_created = df_bsdd[['id', 'createdAt']]
df_bsdd_created = df_bsdd_created[df_bsdd_created['createdAt'] >= date_n_days_ago]
bsdd_created_daily = px.bar(df_bsdd_created.groupby('createdAt').count(), y='id', title="Nombre de BSDD créés par jour",
                            labels={'id': 'Bordereaux de suivi de déchets dangereux',
                                    'createdAt': 'Date de création des bordereaux'})
bsdd_created_total = df_bsdd_created.index.size

# bsdd_status = px.bar(df_bsdd.groupby(by='status').count().sort_values(['id'], ascending=True), x='id',
#              title="Répartition des BSDD par statut")

# nb_sent = df_bsdd.query("status=='SENT'")
df_bsdd_processed = df_bsdd[['id', 'processedAt', 'quantityReceived']]
df_bsdd_processed = df_bsdd_processed[df_bsdd_processed['processedAt'] >= date_n_days_ago]
quantity_processed_daily = px.bar(df_bsdd_processed.groupby(by='processedAt').sum(),
                                  title='Quantité de déchets traitée par jour',
                                  y='quantityReceived',
                                  labels={'quantityReceived': 'Quantité de déchets traitée (tonnes)',
                                          'processedAt': 'Date du traitement des déchets'})
quantity_processed_total = df_bsdd_processed['quantityReceived'].sum().round()

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
                    html.P(f"Total sur la période : {bsdd_created_total} bordereaux"), width=6, align='center'
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id='example-graph2',
                        figure=bsdd_created_daily,
                        config=config
                    ), width=6
                ),
                dbc.Col(
                    html.P(f"Total sur la période : {quantity_processed_total} tonnes"), width=6, align='center'
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
