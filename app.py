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
        'SELECT '
        'id, '
        'status, '
        'date_trunc(\'week\', "default$default"."Form"."createdAt") AS "createdAt", '
        '"Form"."isDeleted", '
        'date_trunc(\'week\', "default$default"."Form"."processedAt") AS "processedAt", '
        '"Form"."wasteDetailsPop", '
        '"Form"."wasteDetailsCode", '
        '"Form"."quantityReceived", '
        '"Form"."recipientProcessingOperation" '
        'FROM "default$default"."Form" '
        'WHERE '
        '"Form"."isDeleted" = FALSE AND "Form"."status" <> \'DRAFT\' '
        # To keep only dangerous waste at query level (not tested):
        # 'AND ("Form"."wasteDetailsCode" LIKE \'%*\' OR "Form"."wasteDetailsPop" = TRUE)'
        'AND "default$default"."Form"."createdAt" < date_trunc(\'week\', CAST(now() AS timestamp)) '
        'AND "default$default"."Form"."processedAt" < date_trunc(\'week\', CAST(now() AS timestamp)) '
        # TODO Think of a bedrock starting date to limit number of results
        'ORDER BY date_trunc(\'week\', "default$default"."Form"."createdAt")',
        con=engine)
    return df_bsdd_query


@cache.memoize(timeout=cache_timeout)
def get_company_data() -> pd.DataFrame:
    df_company_query = pd.read_sql_query(
        'SELECT date_trunc(\'week\', "default$default"."Company"."createdAt") AS "createdAt", count(*) as "count" '
        'FROM "default$default"."Company" '
        'WHERE "default$default"."Company"."createdAt" < date_trunc(\'week\', CAST(now() AS timestamp)) '
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
        'AND "default$default"."User"."createdAt" < date_trunc(\'week\', CAST(now() AS timestamp)) '
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
def normalize_processing_operation(row) -> str:
    string = row['recipientProcessingOperation']
    return string.replace(' ', '') \
               .replace('R0', 'R') \
               .replace('D0', 'D')[:3] \
        .replace('/', '').upper()


# TODO Currenty only the get_blabla_data functions are cached, which means only the db calls are cached.
# Not the dataframe postprocessing, which is always done. Dataframe postprocessing could be added to those functions.

df_bsdd: pd.DataFrame = get_bsdd_data()
df_bsdd = df_bsdd.loc[df_bsdd['createdAt'] >= date_n_days_ago]

# TODO integrate these conversions in parse_dates
df_bsdd['recipientProcessingOperation'] = df_bsdd.apply(lambda row: normalize_processing_operation(row), axis=1)
df_bsdd['createdAt'] = pd.to_datetime(df_bsdd['createdAt'], errors='coerce')
df_bsdd['processedAt'] = pd.to_datetime(df_bsdd['processedAt'], errors='coerce')
print(df_bsdd)

df_bsdd_created_grouped = df_bsdd.groupby(by=['createdAt'], as_index=False).count()
print(df_bsdd_created_grouped)
bsdd_created_weekly = px.line(df_bsdd_created_grouped, y='id', x='createdAt',
                              title="Nombre de bordereaux de suivi de déchets dangereux (BSDD) créés par semaine",
                              labels={'count': 'Bordereaux de suivi de déchets dangereux',
                                      'createdAt': 'Date de création'},
                              markers=True)
bsdd_created_total = df_bsdd.index.size

# bsdd_status = px.bar(df_bsdd.groupby(by='status').count().sort_values(['id'], ascending=True), x='id',
#              title="Répartition des BSDD par statut")

# nb_sent = df_bsdd.query("status=='SENT'")
df_bsdd_processed = df_bsdd.loc[(df_bsdd['processedAt'] >= date_n_days_ago) & (df_bsdd['status'] == 'PROCESSED')]
df_bsdd_processed_grouped = df_bsdd_processed.groupby(by=['processedAt', 'recipientProcessingOperation'],
                                                      as_index=False).sum().round()

quantity_processed_weekly = px.bar(df_bsdd_processed_grouped,
                                   title='Quantité de déchets dangereux traités par semaine',
                                   color='recipientProcessingOperation',
                                   y='quantityReceived',
                                   x='processedAt',
                                   labels={'quantityReceived': 'Quantité de déchets dangereux traités (tonnes)',
                                           'processedAt': 'Date du traitement',
                                           'recipientProcessingOperation': 'Code de traitement'})
quantity_processed_total = df_bsdd_processed_grouped['quantityReceived'].sum()

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
    def fn(input_number) -> str:
        return '{:,.0f}'.format(input_number).replace(',', ' ')

    def unroll_totals(totals: [dict]) -> list:
        result = [html.P(f"Total sur les {time_delta_m} derniers mois")]
        ul_children = []
        for dic in totals:
            ul_children += [html.Li(f"{fn(dic['total'])} {dic['unit']}")]
        result += [html.Ul(ul_children)]
        return result

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
                html.Div(unroll_totals(totals_on_period), className='side-total'),
                width=4, align='center', className='d-flex'
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
        add_figure(company_user_created_weekly, [{'total': company_created_total, 'unit': "établissements inscrits"},
                                                 {'total': user_created_total, 'unit': "utilisateurs inscrits"}],
                   "company_user_created_weekly"),
    ]
                  )

])

if __name__ == '__main__':
    port = getenv('PORT', 8050)

    # Scalingo requires 0.0.0.0 as host, instead of the default 127.0.0.1
    app.run_server(debug=bool(getenv('DEVELOPMENT')), host='0.0.0.0', port=int(port))
