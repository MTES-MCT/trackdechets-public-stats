from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import plotly.io as pio
import plotly.graph_objects as go
import plotly.express as px
from os import getenv

from app import app
import data
import timeconf


company_created_total_life = data.df_company.index.size
user_created_total_life = data.df_user.index.size
quantity_processed_total = data.df_bsdd_processed_grouped["quantityReceived"].sum()
bsdd_created_total = data.df_bsdd_created.index.size

# -----------
# BSDD
# -----------
# def normalize_processing_operation(row) -> str:
#     string = row['recipientProcessingOperation']
#     return string.replace(' ', '') \
#                .replace('R0', 'R') \
#                .replace('D0', 'D')[:3] \
#         .replace('/', '').upper()

config = {"locale": "fr"}

# Override the 'none' template
pio.templates["gouv"] = go.layout.Template(
    layout=dict(
        font=dict(family="Marianne",),
        # title=dict(
        #     font=dict(
        #         color='white',
        #         size=1
        #     )
        # )
    ),
)
pio.templates.default = "none+gouv"

quantity_processed_weekly = px.bar(
    data.df_bsdd_processed_grouped,
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

bsdd_created_weekly = px.line(
    data.df_bsdd_created_grouped,
    y="id",
    x="createdAt",
    title="Bordereaux de suivi de déchets dangereux (BSDD) créés par semaine",
    labels={
        "id": "Bordereaux de suivi de déchets dangereux",
        "createdAt": "Date de création",
    },
    markers=True,
)

company_user_created_weekly = px.line(
    data.df_company_user_created_grouped,
    y="id",
    x="createdAt",
    color="type",
    title="Établissements et utilisateurs inscrits par semaine",
    labels={"id": "Inscriptions", "createdAt": "Date data'inscription", "type": ""},
    markers=True,
)
company_created_total = data.df_company_user_created_grouped.loc[
    data.df_company_user_created_grouped["type"] == "Établissements"
    ]["id"].sum()
user_created_total = data.df_company_user_created_grouped.loc[
    data.df_company_user_created_grouped["type"] == "Utilisateurs"
    ]["id"].sum()

figure_text_tips = {
    "bsdd_processed_weekly": dcc.Markdown(
        """En fin de chaîne, un déchet dangereux est traité. Les **déchets valorisés**
        sont réutilisés (combustion pour du chauffage, recyclage, revente, compostage, etc.)
        tandis que les **déchets éliminés** sont en fin de cycle de vie (enfouissement, stockage,
        traitement chimique, etc.). Plus data'informations sur [
        ecologie.gouv.fr](https://www.ecologie.gouv.fr/traitement-des-dechets). """
    ),
    "bsdd_created_weekly": "",
    "company_user_created_weekly": "",
}


def add_figure(fig, totals_on_period: [dict], fig_id: str) -> dbc.Row:
    """
    Boilerplate for figure rows.
    :param fig: a plotly figure
    :param totals_on_period: sum of values for the given period
    :param fig_id: if of the figure in the resulting HTML
    :return: HTML Row to be added in a Dash layout
    """

    def format_number(input_number) -> str:
        return "{:,.0f}".format(input_number).replace(",", " ")

    def unroll_totals(totals: [dict]) -> list:
        result = [html.P(f"Total sur les {timeconf.time_delta_m} derniers mois")]
        ul_children = []
        for dic in totals:
            ul_children += [
                html.Li(
                    [html.Span(f"{format_number(dic['total'])}"), f" {dic['unit']}"]
                )
            ]
        result += [html.Ul(ul_children)]
        return result

    row = dbc.Row(
        [
            dbc.Col(
                [
                    html.Div(
                        [
                            dcc.Graph(id=fig_id, figure=fig, config=config),
                            figure_text_tips[fig_id],
                            html.Div(
                                unroll_totals(totals_on_period), className="side-total"
                            ),
                        ],
                        className="graph",
                    )
                ],
                width=12,
            )
        ]
    )
    return row


layout = html.Div(
    children=[
        dbc.Container(
            fluid=True,
            children=[
                dbc.Row(
                    [
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
et les déchets data'amiante (DA).

Le contenu de cette page, alimenté par des milliers de bordereaux, est amené à s'enrichir régulièrement
avec de nouvelles statistiques.
                """
                        )
                    ]
                ),
                add_figure(
                    quantity_processed_weekly,
                    [
                        {
                            "total": quantity_processed_total,
                            "unit": "tonnes de déchets dangereux" " traités",
                        }
                    ],
                    "bsdd_processed_weekly",
                ),
                add_figure(
                    bsdd_created_weekly,
                    [{"total": bsdd_created_total, "unit": "bordereaux"}],
                    "bsdd_created_weekly",
                ),
                add_figure(
                    company_user_created_weekly,
                    [
                        {
                            "total": company_created_total,
                            "unit": "établissements inscrits",
                        },
                        {"total": user_created_total, "unit": "utilisateurs inscrits"},
                    ],
                    "company_user_created_weekly",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        html.P("Nombre total data'établissements"),
                                        html.P(company_created_total_life),
                                    ],
                                    className="graph",
                                )
                            ],
                            width=6,
                        ),
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        html.P("Nombre total data'utilisateurs"),
                                        html.P(user_created_total_life),
                                    ],
                                    className="graph",
                                ),
                            ],
                            width=6,
                        ),
                    ]
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

app.layout = layout
server = app.server

if __name__ == "__main__":
    port = getenv("PORT", "8050")

    # Scalingo requires 0.0.0.0 as host, instead of the default 127.0.0.1
    app.run_server(debug=bool(getenv("DEVELOPMENT")), host="0.0.0.0", port=int(port))

