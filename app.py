import dash
from dash import html, dcc
import plotly.express as px
import plotly.io as pio
import pandas as pd
import sqlalchemy
from os import getenv
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
from flask_caching import Cache
import plotly.graph_objects as go
from dotenv import load_dotenv

# Load the environment variables in .env file, or from the host OS if no .env file
load_dotenv()

external_scripts = ['https://cdn.plot.ly/plotly-locale-fr-latest.js']
config = {'locale': 'fr'}

# Use [dbc.themes.BOOTSTRAP] to import the full Bootstrap CSS
app = dash.Dash("trackdechets-public-stats", title='Trackdéchets : statistiques et impact',
                external_stylesheets=[dbc.themes.GRID], external_scripts=external_scripts)

# Override the 'none' template
pio.templates['gouv'] = go.layout.Template(
    layout=dict(
        font=dict(
            family='Marianne',
        ),
    ),
)

pio.templates.default = "none+gouv"

# Flask cache https://dash.plotly.com/performance
# timeout in seconds
cache_timeout = int(getenv('CACHE_TIMEOUT_S'))
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': './cache'
})

# postgresql://admin:admin@localhost:5432/ibnse
engine = sqlalchemy.create_engine(getenv('DATABASE_URL'))


@cache.memoize(timeout=cache_timeout)
def get_bsdd_data() -> pd.DataFrame:
    df_bsdd_query = pd.read_sql_query(
        sqlalchemy.text(
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
            'AND ("default$default"."Form"."wasteDetailsCode" LIKE \'%*%\' '
            'OR "default$default"."Form"."wasteDetailsPop" = TRUE)'
            'AND "default$default"."Form"."createdAt" < date_trunc(\'week\', CAST(now() AS timestamp)) '
            'AND "default$default"."Form"."processedAt" < date_trunc(\'week\', CAST(now() AS timestamp)) '
            # TODO Think of a bedrock starting date to limit number of results
            'ORDER BY date_trunc(\'week\', "default$default"."Form"."createdAt")'),
        con=engine)
    return df_bsdd_query


@cache.memoize(timeout=cache_timeout)
def get_company_data() -> pd.DataFrame:
    df_company_query = pd.read_sql_query(
        'SELECT id, date_trunc(\'week\', "default$default"."Company"."createdAt") AS "createdAt" '
        'FROM "default$default"."Company" '
        'WHERE "default$default"."Company"."createdAt" < date_trunc(\'week\', CAST(now() AS timestamp)) '
        'ORDER BY date_trunc(\'week\', "default$default"."Company"."createdAt")',
        con=engine)
    return df_company_query


@cache.memoize(timeout=cache_timeout)
def get_user_data() -> pd.DataFrame:
    df_user_query = pd.read_sql_query(
        'SELECT id, date_trunc(\'week\', "default$default"."User"."createdAt") AS "createdAt" '
        'FROM "default$default"."User" '
        'WHERE "User"."isActive" = True '
        'AND "default$default"."User"."createdAt" < date_trunc(\'week\', CAST(now() AS timestamp)) '
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
# def normalize_processing_operation(row) -> str:
#     string = row['recipientProcessingOperation']
#     return string.replace(' ', '') \
#                .replace('R0', 'R') \
#                .replace('D0', 'D')[:3] \
#         .replace('/', '').upper()

def normalize_processing_operation(row) -> str:
    string = row['recipientProcessingOperation'].upper()
    if string.startswith('R'):
        return 'Déchet valorisé'
    elif string.startswith('D'):
        return 'Déchet éliminé'
    else:
        return 'Autre'


def normalize_quantity_received(row) -> float:
    quantity = row['quantityReceived']
    if quantity > (int(getenv('SEUIL_DIVISION_QUANTITE')) or 1000):
        quantity = quantity / 1000
    return quantity


# TODO Currenty only the get_blabla_data functions are cached, which means only the db calls are cached.
# Not the dataframe postprocessing, which is always done. Dataframe postprocessing could be added to those functions.

df_bsdd: pd.DataFrame = get_bsdd_data()
df_bsdd = df_bsdd.loc[(df_bsdd['createdAt'] < today) & (df_bsdd['createdAt'] >= date_n_days_ago)]

df_bsdd['recipientProcessingOperation'] = df_bsdd.apply(lambda row: normalize_processing_operation(row), axis=1)
df_bsdd['quantityReceived'] = df_bsdd.apply(lambda row: normalize_quantity_received(row), axis=1)
df_bsdd['createdAt'] = pd.to_datetime(df_bsdd['createdAt'], errors='coerce')
df_bsdd['processedAt'] = pd.to_datetime(df_bsdd['processedAt'], errors='coerce')

df_bsdd_created_grouped = df_bsdd.groupby(by=['createdAt'], as_index=False).count()
bsdd_created_weekly = px.line(df_bsdd_created_grouped, y='id', x='createdAt',
                              title="Bordereaux de suivi de déchets dangereux (BSDD) créés par semaine",
                              labels={'id': 'Bordereaux de suivi de déchets dangereux',
                                      'createdAt': 'Date de création'},
                              markers=True)
bsdd_created_total = df_bsdd.index.size

df_bsdd_processed = df_bsdd.loc[(df_bsdd['processedAt'] < today) & (df_bsdd['processedAt'] >= date_n_days_ago) & (df_bsdd['status'] == 'PROCESSED')]
df_bsdd_processed_grouped = df_bsdd_processed.groupby(by=['processedAt', 'recipientProcessingOperation'],
                                                      as_index=False).sum().round()

quantity_processed_weekly = px.bar(df_bsdd_processed_grouped,
                                   title='Déchets dangereux traités par semaine',
                                   color='recipientProcessingOperation',
                                   y='quantityReceived',
                                   x='processedAt',
                                   labels={'quantityReceived': 'Déchets dangereux traités (tonnes)',
                                           'processedAt': 'Date du traitement',
                                           'recipientProcessingOperation': 'Type de traitement'})
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
df_company_user_created = pd.concat([df_company, df_user], ignore_index=True)

company_created_total_life = df_company.index.size
user_created_total_life = df_user.index.size

df_company_user_created = df_company_user_created.loc[(today > df_company_user_created['createdAt'])
                                                      & (df_company_user_created['createdAt'] >= date_n_days_ago)]
df_company_user_created_grouped = df_company_user_created.groupby(by=['type', 'createdAt'],
                                                                  as_index=False).count()
company_user_created_weekly = px.line(df_company_user_created_grouped,
                                      y='id', x='createdAt', color='type',
                                      title="Établissements et utilisateurs inscrits par semaine",
                                      labels={'id': 'Inscriptions', 'createdAt': 'Date d\'inscription',
                                              'type': ''},
                                      markers=True)
company_created_total = \
    df_company_user_created_grouped.loc[df_company_user_created_grouped['type'] == 'Établissements']['id'].sum()
user_created_total = \
    df_company_user_created_grouped.loc[df_company_user_created_grouped['type'] == 'Utilisateurs']['id'].sum()

figure_text_tips = {
    'bsdd_processed_weekly': dcc.Markdown(
        '''En fin de chaîne, un déchet dangereux est traité. Les **déchets valorisés** sont réutilisés (combustion 
        pour du chauffage, recyclage, revente, compostage, etc.) tandis que les **déchets éliminés** sont en fin de 
        cycle de vie (enfouissement, stockage, traitement chimique, etc.). Plus d'informations sur [
        ecologie.gouv.fr](https://www.ecologie.gouv.fr/traitement-des-dechets). '''
    ),
    'bsdd_created_weekly': '',
    'company_user_created_weekly': ''
}


def add_figure(fig, totals_on_period: [dict], fig_id: str) -> dbc.Row:
    def fn(input_number) -> str:
        return '{:,.0f}'.format(input_number).replace(',', ' ')

    def unroll_totals(totals: [dict]) -> list:
        result = [html.P(f"Total sur les {time_delta_m} derniers mois")]
        ul_children = []
        for dic in totals:
            ul_children += [html.Li(
                [
                    html.Span(f"{fn(dic['total'])}"),
                    f" {dic['unit']}"]
            )]
        result += [html.Ul(ul_children)]
        return result

    row = dbc.Row(
        [
            dbc.Col(
                [
                    html.Div([
                        dcc.Graph(
                            id=fig_id,
                            figure=fig,
                            config=config
                        ),
                        figure_text_tips[fig_id],
                        html.Div(unroll_totals(totals_on_period), className='side-total'),
                    ], className='graph')
                ], width=12
            )
        ]
    )
    return row


app.layout = html.Div(children=[
    dbc.Container(fluid=True, children=[
        dbc.Row(
            [
                dcc.Markdown('''
L'application Trackdéchets est utilisée en France par des milliers de professionnels 
du  déchet pour tracer les déchets dangereux et/ou polluants ([POP](
https://www.ecologie.gouv.fr/polluants-organiques-persistants-pop)) produits, ainsi que différentes 
étapes de leur traçabilité et ce, jusqu'au traitement final. Les déchets traités à l'étranger ne sont 
pas tracés par Trackdéchets. 
        
Un borderau de suivi de déchet (BSD) est créé pour chaque déchet et il contient de nombreuses 
informations (acteurs, déchets, poids, traitement réalisé, etc.). Ces informations sont transmises à 
Trackdéchets par un usage direct ou par API.

Depuis le 1er janvier, l'utilisation de Trackdéchets est obligatoire pour les déchets  dangereux (DD) 
et les déchets d'amiante (DA).

Le contenu de cette page, alimenté par des milliers de bordereaux, est amené à s'enrichir régulièrement 
avec de nouvelles statistiques.
                ''')
            ]
        ),
        add_figure(quantity_processed_weekly, [{'total': quantity_processed_total, 'unit': "tonnes de déchets dangereux"
                                                                                           " traités"}],
                   "bsdd_processed_weekly"),
        add_figure(bsdd_created_weekly, [{'total': bsdd_created_total, 'unit': "bordereaux"}], "bsdd_created_weekly"),
        add_figure(company_user_created_weekly, [{'total': company_created_total, 'unit': "établissements inscrits"},
                                                 {'total': user_created_total, 'unit': "utilisateurs inscrits"}],
                   "company_user_created_weekly"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div([html.P('Nombre total d\'établissements'),
                                  html.P(company_created_total_life)], className='graph')
                    ], width=6
                ),
                dbc.Col(
                    [
                        html.Div([html.P('Nombre total d\'utilisateurs'),
                                  html.P(user_created_total_life)], className='graph'),
                    ], width=6
                ),
            ]
        ),
        dcc.Markdown('Statistiques développées avec [Plotly Dash](https://dash.plotly.com/introduction) ('
                     '[code source](https://github.com/MTES-MCT/trackdechets-public-stats/))', className='source-code')
    ]
                  )

])

if __name__ == '__main__':
    port = getenv('PORT', 8050)

    # Scalingo requires 0.0.0.0 as host, instead of the default 127.0.0.1
    app.run_server(debug=bool(getenv('DEVELOPMENT')), host='0.0.0.0', port=int(port))
