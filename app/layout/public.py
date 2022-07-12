from typing import List

import dash_bootstrap_components as dbc
import plotly.express as px
from app.data.data_extract import get_bsd_data, get_company_data, get_user_data
from app.data.public import (
    get_bsdd_created_df,
    get_bsdd_processed_df,
    get_company_user_data_df,
)
from app.layout.utils import add_callout, add_figure
from dash import dcc, html




def get_public_stats_container() -> List[dbc.Row]:
    """Create all figures needed for the public stats page
    and returns an Dash HTML layout ready to be displayed.
    """

    bsd_data_df = get_bsd_data(include_drafts=False)

    bsdd_created_weekly_df = get_bsdd_created_df(bsd_data_df)

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
    textpositions = [
        "top center" if i % 2 else "bottom center"
        for i in range(bsdd_created_weekly_df.shape[0])
    ]
    bsdd_created_weekly.update_traces(
        {
            "textfont_size": 13,
            "textposition": textpositions,
        }
    )

    bsdd_created_total = bsd_data_df.index.size

    quantity_processed_weekly_df = get_bsdd_processed_df(bsdd_data=bsd_data_df)
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

    company_data_df = get_company_data()
    user_data_df = get_user_data()

    company_created_total = company_data_df[
        company_data_df["createdAt"] >= "2022-01-01"
    ].index.size
    user_created_total = user_data_df[
        user_data_df["createdAt"] >= "2022-01-01"
    ].index.size

    company_created_total_life = company_data_df.index.size
    user_created_total_life = user_data_df.index.size

    company_user_data_df = get_company_user_data_df(company_data_df, user_data_df)

    company_user_created_weekly = px.line(
        company_user_data_df,
        y="id",
        x="createdAt",
        color="type",
        title="Établissements et utilisateurs inscrits par semaine",
        labels={"id": "Inscriptions", "createdAt": "Date d'inscription", "type": ""},
        markers=True,
        text="id",
    )
    company_user_created_weekly.update_traces(textposition="top center")

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
                    text="tonnes de déchets dangereux traités depuis le 1er janvier 2022",
                    width=3,
                ),
                add_callout(
                    number=bsdd_created_total,
                    text="bordereaux créés sur depuis le 1er janvier 2022",
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
                    text="établissements inscrits depuis le 1er janvier 2022",
                    width=3,
                ),
                add_callout(
                    number=company_created_total_life,
                    text="établissements inscrits au total",
                    width=3,
                ),
                add_callout(
                    number=user_created_total,
                    text="utilisateurs inscrits depuis le 1er janvier 2022",
                    width=3,
                ),
                add_callout(
                    number=user_created_total_life,
                    text="utilisateurs inscrits au total",
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
