"""
Dashboard application to publish statistics about Trackdéchets (https://trackdechets.beta.gouv.fr)
"""
from os import getenv
from datetime import datetime, timedelta

from dateutil.tz import UTC
from dash import html, dcc
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
import pandas as pd
import sqlalchemy
import dash_bootstrap_components as dbc
from flask_caching import Cache
from dotenv import load_dotenv
import dash

# Load the environment variables in .env file, or from the host OS if no .env file
load_dotenv()

external_scripts = ["https://cdn.plot.ly/plotly-locale-fr-latest.js"]
config = {"locale": "fr"}

# Use [dbc.themes.BOOTSTRAP] to import the full Bootstrap CSS
app = dash.Dash(
    __name__,
    title="Trackdéchets : statistiques et impact",
    external_stylesheets=[dbc.themes.GRID],
    external_scripts=external_scripts,
)

# Add the @lang attribute to the root <html>
app.index_string = app.index_string.replace('<html>', '<html lang="fr">')

server = app.server

# Override the 'none' template
pio.templates["gouv"] = go.layout.Template(
    layout=dict(
        font=dict(family="Marianne"),
        title=dict(
            font=dict(
                color='black',
                size=22,
                family='Marianne-Bold'
            ),
            x=0.01
        ),
        paper_bgcolor='rgb(238, 238, 238)'
    ),
)

pio.templates.default = "none+gouv"

# Flask cache https://dash.plotly.com/performance
# timeout in seconds
cache_timeout = int(getenv("CACHE_TIMEOUT_S"))
cache = Cache(app.server, config={"CACHE_TYPE": "filesystem", "CACHE_DIR": "./cache"})

# postgresql://admin:admin@localhost:5432/ibnse
engine = sqlalchemy.create_engine(getenv("DATABASE_URL"))


@cache.memoize(timeout=cache_timeout)
def get_bsdd_created() -> pd.DataFrame:
    """
    Queries the configured database for BSDD data, focused on creation date.
    :return: dataframe of BSDD for a given period of time, with their creation week
    """
    df_bsdd_query = pd.read_sql_query(
        sqlalchemy.text(
            "SELECT "
            'date_trunc(\'week\', "default$default"."Form"."createdAt") AS createdAt, '
            # Need id to receive count values upon groupBy
            "id "
            'FROM "default$default"."Form" '
            "WHERE "
            '"Form"."isDeleted" = FALSE AND "Form"."status" <> \'DRAFT\' '
            # To keep only dangerous waste at query level:
            'AND ("default$default"."Form"."wasteDetailsCode" LIKE \'%*%\' '
            'OR "default$default"."Form"."wasteDetailsPop" = TRUE)'
            'AND "default$default"."Form"."createdAt" >= date_trunc(\'week\','
            f"CAST((CAST(now() AS timestamp) + (INTERVAL '-{str(time_delta_m)} month'))"
            "AS timestamp))"
            'AND "default$default"."Form"."createdAt" < date_trunc(\'week\', CAST(now() '
            "AS timestamp)) "
            # TODO Think of a bedrock starting date to limit number of results
            "ORDER BY createdAt"
        ),
        con=engine,
    )

    # By default the column name is createdat (lowercase), strange
    column_name = df_bsdd_query.columns[0]
    df_bsdd_query.rename(columns={column_name: "createdAt"}, inplace=True)
    return df_bsdd_query


@cache.memoize(timeout=cache_timeout)
def get_bsdd_processed() -> pd.DataFrame:
    """
        Queries the configured database for BSDD data, focused on processing date.
        :return: dataframe of BSDD for a given period of time, with their processing week
        """
    df_bsdd_query = pd.read_sql_query(
        sqlalchemy.text(
            "SELECT "
            'date_trunc(\'week\', "default$default"."Form"."processedAt") AS processedAt, '
            '"Form"."status",'
            '"Form"."quantityReceived", '
            '"Form"."recipientProcessingOperation" '
            'FROM "default$default"."Form" '
            "WHERE "
            '"Form"."isDeleted" = FALSE AND "Form"."status" <> \'DRAFT\' '
            # To keep only dangerous waste at query level:
            'AND "default$default"."Form"."processedAt" >= date_trunc(\'week\','
            f"CAST((CAST(now() AS timestamp) + (INTERVAL '-{str(time_delta_m)} month'))"
            " AS timestamp))"
            'AND ("default$default"."Form"."wasteDetailsCode" LIKE \'%*%\' '
            'OR "default$default"."Form"."wasteDetailsPop" = TRUE)'
            'AND "default$default"."Form"."processedAt" < date_trunc(\'week\', CAST(now() AS timestamp)) '
            "ORDER BY processedAt"
        ),
        con=engine,
    )

    # By default the column name is processedat, strange
    column_name = df_bsdd_query.columns[0]
    df_bsdd_query.rename(columns={column_name: "processedAt"}, inplace=True)
    return df_bsdd_query


@cache.memoize(timeout=cache_timeout)
def get_company_data() -> pd.DataFrame:
    """
    Queries the configured database for company data.
    :return: dataframe of companies for a given period of time, with their creation week
    """
    df_company_query = pd.read_sql_query(
        'SELECT id, date_trunc(\'week\', "default$default"."Company"."createdAt") AS "createdAt" '
        'FROM "default$default"."Company" '
        'WHERE "default$default"."Company"."createdAt" < date_trunc(\'week\', CAST(now() AS timestamp)) '
        'ORDER BY date_trunc(\'week\', "default$default"."Company"."createdAt")',
        con=engine,
    )
    return df_company_query


@cache.memoize(timeout=cache_timeout)
def get_user_data() -> pd.DataFrame:
    """
        Queries the configured database for user data, focused on creation date.
        :return: dataframe of users for a given period of time, with their creation week
        """
    df_user_query = pd.read_sql_query(
        'SELECT id, date_trunc(\'week\', "default$default"."User"."createdAt") AS "createdAt" '
        'FROM "default$default"."User" '
        'WHERE "User"."isActive" = True '
        'AND "default$default"."User"."createdAt" < date_trunc(\'week\', CAST(now() AS timestamp)) '
        'ORDER BY date_trunc(\'week\', "default$default"."User"."createdAt")',
        con=engine,
    )
    return df_user_query


time_delta_m = int(getenv("TIME_PERIOD_M"))
time_delta_d = time_delta_m * 30.5
try:
    today = datetime.strptime(getenv("FIXED_TODAY_DATE"), "%Y-%m-%d").replace(
        tzinfo=UTC
    )
    print("Today = " + str(today))
except TypeError:
    print("Today date is not fixed, using datetime.today()")
    today = datetime.today().replace(tzinfo=UTC)
date_n_days_ago = today - timedelta(time_delta_d)


def normalize_processing_operation(row) -> str:
    """Replace waste processing codes with readable labels"""
    string = row["recipientProcessingOperation"].upper()
    if string.startswith("R"):
        return "Déchet valorisé"
    elif string.startswith("D"):
        return "Déchet éliminé"
    return "Autre"


def normalize_quantity_received(row) -> float:
    """Replace weights entered as kg instead of tons"""
    quantity = row["quantityReceived"]
    if quantity > (int(getenv("SEUIL_DIVISION_QUANTITE")) or 1000):
        quantity = quantity / 1000
    return quantity


# TODO Currenty only the get_blabla_data functions are cached, which means
#  only the db calls are cached.
# Not the dataframe postprocessing, which is always done. Dataframe postprocessing could
# be added to those functions.

df_bsdd_created: pd.DataFrame = get_bsdd_created()
df_bsdd_processed: pd.DataFrame = get_bsdd_processed()

df_bsdd_created = df_bsdd_created.loc[
    (df_bsdd_created["createdAt"] < today)
    & (df_bsdd_created["createdAt"] >= date_n_days_ago)
    ]

df_bsdd_processed["recipientProcessingOperation"] = df_bsdd_processed.apply(
    normalize_processing_operation, axis=1
)
df_bsdd_processed["quantityReceived"] = df_bsdd_processed.apply(
    normalize_quantity_received, axis=1
)
df_bsdd_created["createdAt"] = pd.to_datetime(
    df_bsdd_created["createdAt"], errors="coerce", utc=True
)
df_bsdd_processed["processedAt"] = pd.to_datetime(
    df_bsdd_processed["processedAt"], errors="coerce", utc=True
)

df_bsdd_created_grouped = df_bsdd_created.groupby(
    by=["createdAt"], as_index=False
).count()
bsdd_created_weekly = px.line(
    df_bsdd_created_grouped,
    y="id",
    x="createdAt",
    title="Bordereaux de suivi de déchets dangereux (BSDD) créés par semaine",
    labels={
        "id": "Bordereaux de suivi de déchets dangereux",
        "createdAt": "Date de création",
    },
    markers=True,
)
bsdd_created_total = df_bsdd_created.index.size

df_bsdd_processed = df_bsdd_processed.loc[
    (df_bsdd_processed["processedAt"] < today)
    & (df_bsdd_processed["status"] == "PROCESSED")
    ]
df_bsdd_processed_grouped = (
    df_bsdd_processed.groupby(
        by=["processedAt", "recipientProcessingOperation"], as_index=False
    )
        .sum()
        .round()
)

quantity_processed_weekly = px.bar(
    df_bsdd_processed_grouped,
    title="Déchets dangereux traités par semaine",
    color="recipientProcessingOperation",
    y="quantityReceived",
    x="processedAt",
    labels={
        "quantityReceived": "Déchets dangereux traités (tonnes)",
        "processedAt": "Date du traitement",
        "recipientProcessingOperation": "Type de traitement",
    },
)
quantity_processed_total = df_bsdd_processed_grouped["quantityReceived"].sum()

# -----------
# Établissements et utilisateurs
# -----------

df_company = get_company_data()
df_company["type"] = "Établissements"
df_company["createdAt"] = pd.to_datetime(df_company["createdAt"], utc=True)

df_user = get_user_data()
df_user["type"] = "Utilisateurs"
df_user["createdAt"] = pd.to_datetime(df_user["createdAt"], utc=True)
# Concatenate user and company data
df_company_user_created = pd.concat([df_company, df_user], ignore_index=True)

company_created_total_life = df_company.index.size
user_created_total_life = df_user.index.size

df_company_user_created = df_company_user_created.loc[
    (today > df_company_user_created["createdAt"])
    & (df_company_user_created["createdAt"] >= date_n_days_ago)
    ]
df_company_user_created_grouped = df_company_user_created.groupby(
    by=["type", "createdAt"], as_index=False
).count()
company_user_created_weekly = px.line(
    df_company_user_created_grouped,
    y="id",
    x="createdAt",
    color="type",
    title="Établissements et utilisateurs inscrits par semaine",
    labels={"id": "Inscriptions", "createdAt": "Date d'inscription", "type": ""},
    markers=True,
)
company_created_total = df_company_user_created_grouped.loc[
    df_company_user_created_grouped["type"] == "Établissements"
    ]["id"].sum()
user_created_total = df_company_user_created_grouped.loc[
    df_company_user_created_grouped["type"] == "Utilisateurs"
    ]["id"].sum()


def format_number(input_number) -> str:
    return "{:,.0f}".format(input_number).replace(",", " ")


def add_callout(text: str, width: int, sm_width: int = 0, number: int = None):
    text_class = 'number-text' if number else 'fr-callout__text'
    number_class = 'callout-number small-number'
    small_width = width * 2 if sm_width == 0 else sm_width
    if number:
        # Below 1M
        if number < 1000000:
            number_class = 'callout-number'
        # Above 10M
        elif number >= 10000000:
            number_class = 'callout-number smaller-number'
        # From 1M to 10M-1
        # don't change initial value

    col = dbc.Col(
        html.Div([
            html.P(format_number(number), className=number_class) if number else None,
            dcc.Markdown(text, className=text_class)
        ],
            className='fr-callout'),
        width=small_width,
        lg=width)
    return col


def add_figure(fig, fig_id: str) -> dbc.Row:
    """
    Boilerplate for figure rows.
    :param fig: a plotly figure
    :param fig_id: if of the figure in the resulting HTML
    :return: HTML Row to be added in a Dash layout
    """

    row = dbc.Row(
        [
            dbc.Col(
                [
                    html.Div(
                        [
                            dcc.Graph(id=fig_id, figure=fig, config=config)
                        ],
                        className="fr-callout",
                    )
                ],
                width=12,
            )
        ]
    )
    return row


app.layout = html.Div(
    children=[
        dbc.Container(
            fluid=True,
            id='layout-container',
            children=[
                dbc.Row(
                    [
                        dbc.Col([html.H1('Statistiques de Trackdéchets'),
                                 dcc.Markdown(
                                     """
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
                """
                                 )
                                 ], width=12
                                )]),
                html.H2('Déchets dangereux'),
                dbc.Row([
                    add_callout(number=quantity_processed_total,
                                text=f'tonnes de déchets dangereux traités sur {str(time_delta_m)}&nbsp;mois',
                                width=3),
                    add_callout(number=bsdd_created_total,
                                text=f'bordereaux créés sur {str(time_delta_m)}&nbsp;mois',
                                width=3),
                    add_callout(text="""En fin de chaîne, un déchet dangereux est traité. Les **déchets valorisés**
        sont réutilisés (combustion pour du chauffage, recyclage, revente, compostage, etc.)
        tandis que les **déchets éliminés** sont en fin de cycle de vie (enfouissement, stockage,
        traitement chimique, etc.). Plus d'informations sur [
        ecologie.gouv.fr](https://www.ecologie.gouv.fr/traitement-des-dechets). """,
                                width=6)
                ]),
                add_figure(
                    quantity_processed_weekly,
                    "bsdd_processed_weekly",
                ),
                add_figure(
                    bsdd_created_weekly,
                    "bsdd_created_weekly",
                ),
                html.H2('Établissements et utilisateurs'),
                dbc.Row([
                    add_callout(number=company_created_total,
                                text=f'établissements inscrits sur {str(time_delta_m)}&nbsp;mois',
                                width=3),
                    add_callout(number=company_created_total_life,
                                text='établissements inscrits',
                                width=3),
                    add_callout(number=user_created_total,
                                text=f'utilisateurs inscrits sur {str(time_delta_m)}&nbsp;mois',
                                width=3),
                    add_callout(number=user_created_total_life,
                                text='utilisateurs inscrits',
                                width=3),
                ]),
                add_figure(
                    company_user_created_weekly,
                    "company_user_created_weekly",
                ),
                dcc.Markdown(
                    "Statistiques développées avec [Plotly Dash](https://dash.plotly.com/introduction) ("
                    "[code source](https://github.com/MTES-MCT/trackdechets-public-stats/))",
                    className="source-code",
                ),
            ],
        )
    ]
)

if __name__ == "__main__":
    port = getenv("PORT", "8050")

    # Scalingo requires 0.0.0.0 as host, instead of the default 127.0.0.1
    app.run_server(debug=bool(getenv("DEVELOPMENT")), host="0.0.0.0", port=int(port))
