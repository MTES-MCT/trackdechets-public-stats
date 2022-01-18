import dash
from dash import html, dcc
import plotly.express as px
import plotly.io as pio
import pandas as pd
from sqlalchemy import create_engine
from os import getenv
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
from flask_caching import Cache

external_scripts = ['https://cdn.plot.ly/plotly-locale-fr-latest.js']
config = {'locale': 'fr'}

# Use [dbc.themes.BOOTSTRAP] to import the full Bootstrap CSS
app = dash.Dash("trackdechets-public-stats", title='Trackdéchets : statistiques et impact',
                external_stylesheets=[dbc.themes.GRID], external_scripts=external_scripts)
pio.templates.default = "none"

# Flask cache https://dash.plotly.com/performance
# timeout in seconds
cache_timeout = int(getenv('CACHE_TIMEOUT_S'))
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': './cache'
})

# postgresql://admin:admin@localhost:5432/ibnse
engine = create_engine(getenv('DATABASE_URL'))


@cache.memoize(timeout=cache_timeout)
def get_bsdd_data() -> pd.DataFrame:
    df_bsdd_query = pd.read_sql_query(
        'SELECT id, status, cast("Form"."createdAt" as date), "Form"."isDeleted", cast("Form"."processedAt" as date), '
        '"Form"."quantityReceived" FROM "default$default"."Form" '
        'WHERE "Form"."isDeleted" = FALSE AND "Form"."status" <> \'DRAFT\'',
        con=engine)
    return df_bsdd_query


@cache.memoize(timeout=cache_timeout)
def get_company_data() -> pd.DataFrame:
    df_company_query = pd.read_sql_query(
        'SELECT id, cast("Company"."createdAt" as date)'
        'FROM "default$default"."Company" ',
        con=engine)
    return df_company_query


@cache.memoize(timeout=cache_timeout)
def get_user_data() -> pd.DataFrame:
    df_user_query = pd.read_sql_query(
        'SELECT id, cast("User"."createdAt" as date)'
        'FROM "default$default"."User" '
        'WHERE "User"."isActive" = True',
        con=engine)
    return df_user_query


#  2020-10-26 14:52:54.995 ===> 2020-10-26
# df_bsdd['createdAt'] = df_bsdd['createdAt'].dt.date
# df_bsdd['processedAt'] = df_bsdd['processedAt'].dt.date

time_delta = int(getenv('TIME_PERIOD_D'))
date_n_days_ago = datetime.date(datetime.today() - timedelta(time_delta))

# -----------
# BSDD
# -----------

df_bsdd: pd.DataFrame = get_bsdd_data()
df_bsdd_created = df_bsdd[['id', 'createdAt']]
df_bsdd_created = df_bsdd_created.loc[(datetime.date(datetime.today()) > df_bsdd_created['createdAt'])
                                      & (df_bsdd_created['createdAt'] >= date_n_days_ago)]
bsdd_created_daily = px.line(df_bsdd_created.groupby('createdAt').count(), y='id',
                             title="Nombre de bordereaux de suivi de déchets dangereux (BSDD) créés par jour",
                             labels={'id': 'Bordereaux de suivi de déchets dangereux',
                                     'createdAt': 'Date de création'},
                             markers=True)
bsdd_created_total = df_bsdd_created.index.size

# bsdd_status = px.bar(df_bsdd.groupby(by='status').count().sort_values(['id'], ascending=True), x='id',
#              title="Répartition des BSDD par statut")

# nb_sent = df_bsdd.query("status=='SENT'")
df_bsdd_processed = df_bsdd[['id', 'processedAt', 'quantityReceived']]
df_bsdd_processed = df_bsdd_processed[(datetime.date(datetime.today()) > df_bsdd_processed['processedAt'])
                                      & (df_bsdd_processed['processedAt'] >= date_n_days_ago)]
quantity_processed_daily = px.line(df_bsdd_processed.groupby(by='processedAt').sum(),
                                   title='Quantité de déchets traitée par jour',
                                   y='quantityReceived',
                                   labels={'quantityReceived': 'Quantité de déchets traitée (tonnes)',
                                           'processedAt': 'Date du traitement'},
                                   markers=True)
quantity_processed_total = df_bsdd_processed['quantityReceived'].sum().round()

# -----------
# Établissements et utilisateurs
# -----------

df_company = get_company_data()
df_company['type'] = 'Établissements'
df_user = get_user_data()
df_user['type'] = 'Utilisateurs'
df_company_created = df_company.loc[(datetime.date(datetime.today()) > df_company['createdAt'])
                                    & (df_company['createdAt'] >= date_n_days_ago)]
df_user_created = df_user.loc[(datetime.date(datetime.today()) > df_user['createdAt'])
                              & (df_user['createdAt'] >= date_n_days_ago)]
df_company_user_created = pd.concat([df_company_created, df_user_created], ignore_index=True)
company_user_created_daily = px.line(df_company_user_created.groupby(['createdAt', 'type'], as_index=False).count(),
                                     y='id', x='createdAt', color='type',
                                     title="Établissements et utilisateurs inscrits par jour",
                                     labels={'id': 'Inscriptions', 'createdAt': 'Date d\'inscription'},
                                     markers=True)
company_created_total = df_company_created.index.size
user_created_total = df_user_created.index.size


def add_figure(fig, totals_on_period: [dict], fig_id: str) -> dbc.Row:
    def unroll_totals(totals: [dict]) -> list:
        result = []
        for dic in totals:
            result += [html.Li(f"{dic['total']} {dic['unit']}")]
        return [f"Total sur les {time_delta} derniers jours : ", html.Ul(result)]

    row = dbc.Row(
        [
            dbc.Col(
                dcc.Graph(
                    id=fig_id,
                    figure=fig,
                    config=config
                ), width=8
            ),
            dbc.Col(
                html.P(unroll_totals(totals_on_period)), width=4, align='center'
            )
        ]
    )
    return row


app.layout = html.Div(children=[
    dbc.Container(fluid=True, children=[
        dbc.Row(
            [
                html.P("L'application Trackdéchets est utilisée en France par des milliers de professionnels du "
                       "déchet pour déclarer les déchets produits, ainsi que les différentes manipulations, jusqu'au "
                       "traitement final."),
                html.P("Un borderau de suivi de déchet (BSD) est créé pour chaque conteneur (sac, baril, "
                       "bidon, etc.) ou groupement de conteneurs. De nombreuses informations telles que le type de "
                       "déchet, le poids, et les enteprises impliquées sont envoyées à Trackdéchets."),
                html.P("Aujourd'hui, l'utilisation de Trackdéchets est obligatoire pour les déchets dangereux (DD) et "
                       "les déchets d'amiante (DA)."),
                html.P("Le contenu de cette page est amené à s'enrichir régulièrement avec de nouvelles statistiques.")
            ]
        ),
        add_figure(quantity_processed_daily, [{'total': quantity_processed_total, 'unit': "tonnes"}],
                   "bsdd_processed_daily"),
        add_figure(bsdd_created_daily, [{'total': bsdd_created_total, 'unit': "bordereaux"}], "bsdd_created_daily"),
        add_figure(company_user_created_daily, [{'total': company_created_total, 'unit': "établissements"},
                                                {'total': user_created_total, 'unit': "utilisateurs"}],
                   "company_user_created_daily"),
    ]
                  )

])

if __name__ == '__main__':
    port = getenv('PORT', 8050)

    # Scalingo requires 0.0.0.0 as host, instead of the default 127.0.0.1
    app.run_server(debug=not getenv('PRODUCTION'), host='0.0.0.0', port=int(port))
