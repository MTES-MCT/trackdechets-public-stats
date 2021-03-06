from dash import html, dcc, callback, Input, Output
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

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


bsdd_created_weekly = px.line(
    app.data.get_bsdd_created_df(),
    y="id",
    x="createdAt",
    title="Bordereaux de suivi de d??chets dangereux (BSDD) cr????s par semaine",
    labels={
        "id": "Bordereaux de suivi de d??chets dangereux",
        "createdAt": "Date de cr??ation",
    },
    markers=True,
    text="id"

)
bsdd_created_weekly.update_traces(textposition="top center")

bsdd_created_total = app.data.get_bsdd_created().index.size

quantity_processed_weekly = px.bar(
    app.data.get_bsdd_processed_df(),
    title="D??chets dangereux trait??s par semaine",
    color="recipientProcessingOperation",
    y="quantityReceived",
    x="processedAt",
    text="quantityReceived",
    labels={
        "quantityReceived": "D??chets dangereux trait??s (tonnes)",
        "processedAt": "Date du traitement",
        "recipientProcessingOperation": "Type de traitement",
    },
)

quantity_processed_total = app.data.get_bsdd_processed_df()["quantityReceived"].sum()

company_created_total_life = app.data.get_company_data().index.size
user_created_total_life = app.data.get_user_data().index.size

company_user_created_weekly = px.line(
    app.data.get_company_user_data_df(),
    y="id",
    x="createdAt",
    color="type",
    title="??tablissements et utilisateurs inscrits par semaine",
    labels={"id": "Inscriptions", "createdAt": "Date d'inscription", "type": ""},
    markers=True,
    text="id"
)
company_user_created_weekly.update_traces(textposition="top center")

company_created_total = app.data.get_company_user_data_df().loc[
    app.data.get_company_user_data_df()["type"] == "??tablissements"
    ]["id"].sum()
user_created_total = app.data.get_company_user_data_df().loc[
    app.data.get_company_user_data_df()["type"] == "Utilisateurs"
    ]["id"].sum()

public_stats_container = [
    dbc.Row(
        [
            dbc.Col([html.H1('Statistiques de Trackd??chets'),
                     dcc.Markdown(
                         """
L'application Trackd??chets est utilis??e en France par des milliers de professionnels
du  d??chet pour tracer les d??chets dangereux et/ou polluants ([POP](
https://www.ecologie.gouv.fr/polluants-organiques-persistants-pop)) produits, ainsi que diff??rentes
??tapes de leur tra??abilit?? et ce, jusqu'au traitement final. Les d??chets trait??s ?? l'??tranger ne sont
pas trac??s par Trackd??chets.

Un borderau de suivi de d??chet (BSD) est cr???? pour chaque d??chet et il contient de nombreuses
informations (acteurs, d??chets, poids, traitement r??alis??, etc.). Ces informations sont transmises ??
Trackd??chets par un usage direct ou par API.

Depuis le 1er janvier, l'utilisation de Trackd??chets est obligatoire pour les d??chets  dangereux (DD)
et les d??chets d'amiante (DA).

Le contenu de cette page, aliment?? par des milliers de bordereaux, est amen?? ?? s'enrichir r??guli??rement
avec de nouvelles statistiques.
                """
                     )
                     ], width=12
                    )]),
    html.H2('D??chets dangereux'),
    dbc.Row([
        add_callout(number=quantity_processed_total,
                    text=f'tonnes de d??chets dangereux trait??s sur {str(time_delta_m)}&nbsp;mois',
                    width=3),
        add_callout(number=bsdd_created_total,
                    text=f'bordereaux cr????s sur {str(time_delta_m)}&nbsp;mois',
                    width=3),
        add_callout(text="""En fin de cha??ne, un d??chet dangereux est trait??. Les **d??chets valoris??s**
        sont r??utilis??s (combustion pour du chauffage, recyclage, revente, compostage, etc.)
        tandis que les **d??chets ??limin??s** sont en fin de cycle de vie (enfouissement, stockage,
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
    html.H2('??tablissements et utilisateurs'),
    dbc.Row([
        add_callout(number=company_created_total,
                    text=f'??tablissements inscrits sur {str(time_delta_m)}&nbsp;mois',
                    width=3),
        add_callout(number=company_created_total_life,
                    text='??tablissements inscrits',
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
        "Statistiques d??velopp??es avec [Plotly Dash](https://dash.plotly.com/introduction) ("
        "[code source](https://github.com/MTES-MCT/trackdechets-public-stats/))",
        className="source-code",
    ),
]

#################################################################################
#
#                   Internal stats figures and container
#
##################################################################################

# Created BSDD
internal_bsdd_created_week = px.line(app.data.get_recent_bsdd_created_week(), x="createdAt", y="count", text="count",
                                     title="BSDD cr????s par semaine",
                                     labels={
                                         "count": "BSDD cr????s",
                                         "createdAt": "Semaine de cr??ation",
                                     },
                                     markers=True, )
internal_bsdd_created_week.update_traces(textposition="bottom right")

# Sent BSDD
internal_bsdd_sent_week = px.line(app.data.get_recent_bsdd_sent(), x="sentAt", y="count", text="count",
                                  title="BSDD enlev??s par semaine",
                                  labels={
                                      "count": "BSDD enlev??s",
                                      "sentAt": "Semaine d'enl??vement",
                                  },
                                  markers=True, )
internal_bsdd_sent_week.update_traces(textposition="bottom right")

# Received BSDD
internal_bsdd_received_week = px.line(app.data.get_recent_bsdd_received(), x="receivedAt", y="count", text="count",
                                      title="BSDD r??ceptionn??s par semaine",
                                      labels={
                                          "count": "BSDD r??ceptionn??s",
                                          "receivedAt": "Semaine de r??ception",
                                      },
                                      markers=True, )
internal_bsdd_received_week.update_traces(textposition="bottom right")

internal_stats_container = [
    dbc.Row(
        dbc.Col(
            [html.H1('Statistiques de mont??e en charge de Trackd??chets'),
             html.H2('Bordereaux de suivi de d??chets dangereux (BSDD)'), ]
        )
    ),
    dbc.Row(
        dbc.Col(
            [
                add_figure(internal_bsdd_created_week, 'internal_bsdd_created_week')
            ],
            width=10)
    ),
    dbc.Row(
        dbc.Col(
            [
                add_figure(internal_bsdd_sent_week, 'internal_bsdd_sent_week')
            ],
            width=10)
    ),
    dbc.Row(
        dbc.Col(
            [
                add_figure(internal_bsdd_received_week, 'internal_bsdd_received_week')
            ],
            width=10)
    ),

]


# Router
@callback(Output('layout-container', 'children'),
          [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return public_stats_container
    elif pathname == '/internal-stats':
        return internal_stats_container
    else:
        return 'Page inconnue : "' + pathname + '"'


dash_app.layout = html.Main(
    children=[
        dcc.Location(id='url', refresh=False),
        dbc.Container(
            fluid=True,
            id='layout-container',
            children=[]
        )
    ]
)
