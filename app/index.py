from dash import html, dcc
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from os import getenv

from app.app import dash_app, extra_config
from app.time_config import time_delta_m
import app.data

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
        paper_bgcolor='rgb(238, 238, 238)',
        colorway=['#2F4077', '#a94645', '#8D533E', '#417DC4'],
        yaxis=dict(
            tickformat=',0f',
            separatethousands=True,
        )
    ),
)

pio.templates.default = "none+gouv"

bsdd_created_weekly = px.line(
    app.data.df_bsdd_created_grouped,
    y="id",
    x="createdAt",
    title="Bordereaux de suivi de déchets dangereux (BSDD) créés par semaine",
    labels={
        "id": "Bordereaux de suivi de déchets dangereux",
        "createdAt": "Date de création",
    },
    markers=True,
    text="id"

)
bsdd_created_weekly.update_traces(textposition="top center")

bsdd_created_total = app.data.df_bsdd_created.index.size

quantity_processed_weekly = px.bar(
    app.data.df_bsdd_processed_grouped,
    title="Déchets dangereux traités par semaine",
    color="recipientProcessingOperation",
    y="quantityReceived",
    x="processedAt",
    text="quantityReceived",
    labels={
        "quantityReceived": "Déchets dangereux traités (tonnes)",
        "processedAt": "Date du traitement",
        "recipientProcessingOperation": "Type de traitement",
    },
)

quantity_processed_total = app.data.df_bsdd_processed_grouped["quantityReceived"].sum()

company_created_total_life = app.data.df_company.index.size
user_created_total_life = app.data.df_user.index.size

company_user_created_weekly = px.line(
    app.data.df_company_user_created_grouped,
    y="id",
    x="createdAt",
    color="type",
    title="Établissements et utilisateurs inscrits par semaine",
    labels={"id": "Inscriptions", "createdAt": "Date d'inscription", "type": ""},
    markers=True,
    text="id"
)
company_user_created_weekly.update_traces(textposition="top center")


company_created_total = app.data.df_company_user_created_grouped.loc[
    app.data.df_company_user_created_grouped["type"] == "Établissements"
    ]["id"].sum()
user_created_total = app.data.df_company_user_created_grouped.loc[
    app.data.df_company_user_created_grouped["type"] == "Utilisateurs"
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
        lg=width,
        class_name='flex')
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
                            dcc.Graph(id=fig_id, figure=fig, config=extra_config)
                        ],
                        className="fr-callout",
                    )
                ],
                width=12,
            )
        ]
    )
    return row


dash_app.layout = html.Main(
    children=[
        dcc.Location(id='url', refresh=False),
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



