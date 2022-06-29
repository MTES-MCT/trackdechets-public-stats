import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from dash import Input, Output, callback, dcc, html

from app.data import (
    get_bsdd_created_df,
    get_bsdd_data,
    get_bsdd_processed_df,
    get_company_data,
    get_company_user_data_df,
    get_recent_bsdd_created_week,
    get_recent_bsdd_received,
    get_recent_bsdd_sent,
    get_user_data,
)
from app.time_config import time_delta_m

# Override the 'none' template
pio.templates["gouv"] = go.layout.Template(
    layout=dict(
        font=dict(family="Marianne"),
        title=dict(font=dict(color="black", size=22, family="Marianne-Bold"), x=0.01),
        paper_bgcolor="rgb(238, 238, 238)",
        colorway=["#2F4077", "#a94645", "#8D533E", "#417DC4"],
        yaxis=dict(
            tickformat=",0f",
            separatethousands=True,
        ),
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
                        [dcc.Graph(id=fig_id, figure=fig, config={"locale": "fr"})],
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
    text_class = "number-text" if number else "fr-callout__text"
    number_class = "callout-number small-number"
    small_width = width * 2 if sm_width == 0 else sm_width
    if number:
        # Below 1M
        if number < 1000000:
            number_class = "callout-number"
        # Above 10M
        elif number >= 10000000:
            number_class = "callout-number smaller-number"
        # From 1M to 10M-1
        # don't change initial value

    col = dbc.Col(
        html.Div(
            [
                html.P(format_number(number), className=number_class)
                if number
                else None,
                dcc.Markdown(text, className=text_class),
            ],
            className="fr-callout",
        ),
        width=small_width,
        lg=width,
        class_name="flex",
    )
    return col


#################################################################################
#
#                   Internal stats figures and container
#
##################################################################################

# Created BSDD
internal_bsdd_created_week = px.line(
    get_recent_bsdd_created_week(),
    x="createdAt",
    y="count",
    text="count",
    title="BSDD créés par semaine",
    labels={
        "count": "BSDD créés",
        "createdAt": "Semaine de création",
    },
    markers=True,
)
internal_bsdd_created_week.update_traces(textposition="bottom right")

# Sent BSDD
internal_bsdd_sent_week = px.line(
    get_recent_bsdd_sent(),
    x="sentAt",
    y="count",
    text="count",
    title="BSDD enlevés par semaine",
    labels={
        "count": "BSDD enlevés",
        "sentAt": "Semaine d'enlèvement",
    },
    markers=True,
)
internal_bsdd_sent_week.update_traces(textposition="bottom right")

# Received BSDD
internal_bsdd_received_week = px.line(
    get_recent_bsdd_received(),
    x="receivedAt",
    y="count",
    text="count",
    title="BSDD réceptionnés par semaine",
    labels={
        "count": "BSDD réceptionnés",
        "receivedAt": "Semaine de réception",
    },
    markers=True,
)
internal_bsdd_received_week.update_traces(textposition="bottom right")

internal_stats_container = [
    dbc.Row(
        dbc.Col(
            [
                html.H1("Statistiques de montée en charge de Trackdéchets"),
                html.H2("Bordereaux de suivi de déchets dangereux (BSDD)"),
            ]
        )
    ),
    dbc.Row(
        dbc.Col(
            [add_figure(internal_bsdd_created_week, "internal_bsdd_created_week")],
            width=10,
        )
    ),
    dbc.Row(
        dbc.Col(
            [add_figure(internal_bsdd_sent_week, "internal_bsdd_sent_week")], width=10
        )
    ),
    dbc.Row(
        dbc.Col(
            [add_figure(internal_bsdd_received_week, "internal_bsdd_received_week")],
            width=10,
        )
    ),
]


# Router
# @callback(Output("layout-container", "children"), [Input("url", "pathname")])
# def display_page(pathname):
#     if pathname == "/":
#         return public_stats_container
#     elif pathname == "/internal-stats":
#         return internal_stats_container
#     else:
#         return 'Page inconnue : "' + pathname + '"'


def get_public_stats_container():

    bsdd_data_df = get_bsdd_data()

    bsdd_created_weekly_df = get_bsdd_created_df(bsdd_data_df)

    bsdd_created_weekly = px.line(
        bsdd_created_weekly_df,
        y="id",
        x="createdAt",
        title="Bordereaux de suivi de déchets dangereux (BSDD) créés par semaine",
        labels={
            "id": "Bordereaux de suivi de déchets dangereux",
            "createdAt": "Date de création",
        },
        markers=True,
        text="id",
    )
    bsdd_created_weekly.update_traces(textposition="top center")

    bsdd_created_total = bsdd_data_df.id.nunique()

    quantity_processed_weekly_df = get_bsdd_processed_df(bsdd_data=bsdd_data_df)
    quantity_processed_weekly = px.bar(
        quantity_processed_weekly_df,
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

    quantity_processed_total = quantity_processed_weekly_df["quantityReceived"].sum()

    company_created_total_life = get_company_data().index.size
    user_created_total_life = get_user_data().index.size

    company_user_created_weekly = px.line(
        get_company_user_data_df(),
        y="id",
        x="createdAt",
        color="type",
        title="Établissements et utilisateurs inscrits par semaine",
        labels={"id": "Inscriptions", "createdAt": "Date d'inscription", "type": ""},
        markers=True,
        text="id",
    )
    company_user_created_weekly.update_traces(textposition="top center")

    company_created_total = (
        get_company_user_data_df()
        .loc[get_company_user_data_df()["type"] == "Établissements"]["id"]
        .sum()
    )
    user_created_total = (
        get_company_user_data_df()
        .loc[get_company_user_data_df()["type"] == "Utilisateurs"]["id"]
        .sum()
    )

    public_stats_container = [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1("Statistiques de Trackdéchets"),
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
                        ),
                    ],
                    width=12,
                )
            ]
        ),
        html.H2("Déchets dangereux"),
        dbc.Row(
            [
                add_callout(
                    number=quantity_processed_total,
                    text=f"tonnes de déchets dangereux traités sur {str(time_delta_m)}&nbsp;mois",
                    width=3,
                ),
                add_callout(
                    number=bsdd_created_total,
                    text=f"bordereaux créés sur {str(time_delta_m)}&nbsp;mois",
                    width=3,
                ),
                add_callout(
                    text="""En fin de chaîne, un déchet dangereux est traité. Les **déchets valorisés**
        sont réutilisés (combustion pour du chauffage, recyclage, revente, compostage, etc.)
        tandis que les **déchets éliminés** sont en fin de cycle de vie (enfouissement, stockage,
        traitement chimique, etc.). Plus d'informations sur [
        ecologie.gouv.fr](https://www.ecologie.gouv.fr/traitement-des-dechets). """,
                    width=6,
                ),
            ]
        ),
        add_figure(
            quantity_processed_weekly,
            "bsdd_processed_weekly",
        ),
        add_figure(
            bsdd_created_weekly,
            "bsdd_created_weekly",
        ),
        html.H2("Établissements et utilisateurs"),
        dbc.Row(
            [
                add_callout(
                    number=company_created_total,
                    text=f"établissements inscrits sur {str(time_delta_m)}&nbsp;mois",
                    width=3,
                ),
                add_callout(
                    number=company_created_total_life,
                    text="établissements inscrits",
                    width=3,
                ),
                add_callout(
                    number=user_created_total,
                    text=f"utilisateurs inscrits sur {str(time_delta_m)}&nbsp;mois",
                    width=3,
                ),
                add_callout(
                    number=user_created_total_life,
                    text="utilisateurs inscrits",
                    width=3,
                ),
            ]
        ),
        add_figure(
            company_user_created_weekly,
            "company_user_created_weekly",
        ),
        dcc.Markdown(
            "Statistiques développées avec [Plotly Dash](https://dash.plotly.com/introduction) ("
            "[code source](https://github.com/MTES-MCT/trackdechets-public-stats/))",
            className="source-code",
        ),
    ]
    return public_stats_container


def serve_layout() -> html:
    print("layout served")
    layout = html.Main(
        children=[
            # dcc.Location(id="url", refresh=False),
            dbc.Container(
                fluid=True, id="layout-container", children=get_public_stats_container()
            ),
        ]
    )

    return layout
