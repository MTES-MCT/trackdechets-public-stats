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
def get_bsdd_created_data() -> pd.DataFrame:
    df_bsdd_created_query = pd.read_sql_query(
        'SELECT date_trunc(\'week\', "default$default"."Form"."createdAt") AS "createdAt", count(*) AS "count" '
        'FROM "default$default"."Form" '
        'WHERE "Form"."isDeleted" = FALSE AND "Form"."status" <> \'DRAFT\' '
        'GROUP BY date_trunc(\'week\', "default$default"."Form"."createdAt") '
        'ORDER BY date_trunc(\'week\', "default$default"."Form"."createdAt")',
        con=engine)
    return df_bsdd_created_query


@cache.memoize(timeout=cache_timeout)
def get_bsdd_processed_data() -> pd.DataFrame:
    df_bsdd_processed_query = pd.read_sql_query(
        'SELECT date_trunc(\'week\', "default$default"."Form"."processedAt") AS "processedAt", '
        'sum("default$default"."Form"."quantityReceived") AS "quantityReceived"  '
        'FROM "default$default"."Form" '
        'WHERE "Form"."isDeleted" = FALSE AND "Form"."status" <> \'DRAFT\''
        'GROUP BY date_trunc(\'week\', "default$default"."Form"."processedAt") '
        'ORDER BY date_trunc(\'week\', "default$default"."Form"."processedAt")',
        con=engine)
    return df_bsdd_processed_query


@cache.memoize(timeout=cache_timeout)
def get_company_data() -> pd.DataFrame:
    df_company_query = pd.read_sql_query(
        'SELECT date_trunc(\'week\', "default$default"."Company"."createdAt") AS "createdAt", count(*) as "count" '
        'FROM "default$default"."Company" '
        'GROUP BY date_trunc(\'week\', "default$default"."Company"."createdAt") '
        'ORDER BY date_trunc(\'week\', "default$default"."Company"."createdAt")',
        con=engine)
    return df_company_query


@cache.memoize(timeout=cache_timeout)
def get_user_data() -> pd.DataFrame:
    df_user_query = pd.read_sql_query(
        'SELECT date_trunc(\'week\', "default$default"."User"."createdAt") AS "createdAt", count(*) as "count" '
        'FROM "default$default"."User" '
        'WHERE "User"."isActive" = True '
        'GROUP BY date_trunc(\'week\', "default$default"."User"."createdAt") '
        'ORDER BY date_trunc(\'week\', "default$default"."User"."createdAt")',
        con=engine)
    return df_user_query


time_delta_m = int(getenv('TIME_PERIOD_M'))
time_delta_d = time_delta_m * 30.5
try:
    today = datetime.strptime(getenv('FIXED_TODAY_DATE'), '%Y-%m-%d')
except TypeError:
    print('Today date is not fixed, using datetime.today()')
    today = datetime.today()
date_n_days_ago = today - timedelta(time_delta_d)

# -----------
# BSDD
# -----------

df_bsdd_created: pd.DataFrame = get_bsdd_created_data()
# TODO integrate these conversions in parse_dates
df_bsdd_created['createdAt'] = pd.to_datetime(df_bsdd_created['createdAt'], errors='coerce')

df_bsdd_created = df_bsdd_created.loc[(today > df_bsdd_created['createdAt'])
                                      & (df_bsdd_created['createdAt'] >= date_n_days_ago)]
print(df_bsdd_created)
bsdd_created_weekly = px.line(df_bsdd_created, y='count', x='createdAt',
                              title="Nombre de bordereaux de suivi de déchets dangereux (BSDD) créés par semaine",
                              labels={'count': 'Bordereaux de suivi de déchets dangereux',
                                      'createdAt': 'Date de création'},
                              markers=True)
bsdd_created_total = df_bsdd_created['count'].sum()

# bsdd_status = px.bar(df_bsdd.groupby(by='status').count().sort_values(['id'], ascending=True), x='id',
#              title="Répartition des BSDD par statut")

# nb_sent = df_bsdd.query("status=='SENT'")

df_bsdd_processed = get_bsdd_processed_data()
df_bsdd_processed['processedAt'] = pd.to_datetime(df_bsdd_processed['processedAt'], errors='coerce')
df_bsdd_processed = df_bsdd_processed[(today > df_bsdd_processed['processedAt'])
                                      & (df_bsdd_processed['processedAt'] >= date_n_days_ago)]
print(df_bsdd_processed)

quantity_processed_weekly = px.line(df_bsdd_processed,
                                    title='Quantité de déchets traitée par semaine',
                                    y='quantityReceived',
                                    x='processedAt',
                                    labels={'quantityReceived': 'Quantité de déchets traitée (tonnes)',
                                            'processedAt': 'Date du traitement'},
                                    markers=True)
quantity_processed_total = df_bsdd_processed['quantityReceived'].sum().round()

# -----------
# Établissements et utilisateurs
# -----------

df_company = get_company_data()
df_company['type'] = 'Établissements'
df_company['createdAt'] = pd.to_datetime(df_company['createdAt'])
df_user = get_user_data()
df_user['type'] = 'Utilisateurs'
df_user['createdAt'] = pd.to_datetime(df_user['createdAt'])
print(df_user)
print(df_company)
df_company_user_created = pd.concat([df_company, df_user], ignore_index=True)
df_company_user_created = df_company_user_created.loc[(today > df_company_user_created['createdAt'])
                                                      & (df_company_user_created['createdAt'] >= date_n_days_ago)]
print(df_company_user_created)
company_user_created_weekly = px.line(df_company_user_created,
                                      y='count', x='createdAt', color='type',
                                      title="Établissements et utilisateurs inscrits par semaine",
                                      labels={'id': 'Inscriptions', 'createdAt': 'Date d\'inscription'},
                                      markers=True)
company_created_total = df_company_user_created.loc[df_company_user_created['type'] == 'Établissements']['count'].sum()
user_created_total = df_company_user_created.loc[df_company_user_created['type'] == 'Utilisateurs']['count'].sum()


def add_figure(fig, totals_on_period: [dict], fig_id: str) -> dbc.Row:
    def unroll_totals(totals: [dict]) -> list:
        result = []
        for dic in totals:
            result += [html.Li(f"{dic['total']} {dic['unit']}")]
        return [f"Total sur les {time_delta_m} derniers mois : ", html.Ul(result)]

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
                html.P(["L'application Trackdéchets est utilisée en France par des milliers de professionnels du "
                        "déchet pour tracer les déchets dangereux et/ou polluants (",
                        html.A("POP", href='https://www.ecologie.gouv.fr/polluants-organiques-persistants-pop'),
                        ") produits, ainsi que les différentes étapes de leur traçabilité et ce, jusqu'au traitement "
                        "final. Les déchets traités à l'étranger ne sont pas tracés par Trackdéchets."]),
                html.P("Un borderau de suivi de déchet (BSD) est créé pour chaque déchet et il contient de nombreuses "
                       "informations (acteurs, déchets, poids, traitement réalisé etc.). Ces informations sont "
                       "transmises à Trackdéchets par un usage direct ou par API. "),
                html.P("Depuis le 1er janvier, l'utilisation de Trackdéchets est obligatoire pour les déchets "
                       "dangereux (DD) et les déchets d'amiante (DA)."),
                html.P("Le contenu de cette page, alimenté par des milliers de bordereaux, est amené à s'enrichir "
                       "régulièrement avec de nouvelles statistiques.")
            ]
        ),
        add_figure(quantity_processed_weekly, [{'total': quantity_processed_total, 'unit': "tonnes"}],
                   "bsdd_processed_weekly"),
        add_figure(bsdd_created_weekly, [{'total': bsdd_created_total, 'unit': "bordereaux"}], "bsdd_created_weekly"),
        add_figure(company_user_created_weekly, [{'total': company_created_total, 'unit': "établissements"},
                                                 {'total': user_created_total, 'unit': "utilisateurs"}],
                   "company_user_created_weekly"),
    ]
                  )

])

if __name__ == '__main__':
    port = getenv('PORT', 8050)

    # Scalingo requires 0.0.0.0 as host, instead of the default 127.0.0.1
    app.run_server(debug=bool(getenv('DEVELOPMENT')), host='0.0.0.0', port=int(port))
