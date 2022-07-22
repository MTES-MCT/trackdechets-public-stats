from turtle import width
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from app.layout.utils import add_callout, add_figure
from dash import dcc, html


def create_public_stats_container(
    quantity_processed_total: int,
    bsdd_created_total: int,
    quantity_processed_weekly: go.Figure,
    bsdd_created_weekly: go.Figure,
    bsda_created_weekly: go.Figure,
    bsff_created_weekly: go.Figure,
    bsdasri_created_weekly: go.Figure,
    company_created_total: int,
    company_created_total_life: int,
    user_created_total: int,
    user_created_total_life: int,
    company_created_weekly: go.Figure,
    user_created_weekly: go.Figure,
):
    container = [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1("Statistiques de Trackdéchets"),
                        dcc.Markdown(
                            """
L'application Trackdéchets est utilisée en France par des milliers de professionnels
du déchet pour tracer plusieurs types de déchets:
- déchets dangereux et/ou polluants ([POP](https://www.ecologie.gouv.fr/polluants-organiques-persistants-pop)) ;
- déchets d'amiantes ;
- fluides frigorigènes ;
- déchets d'activités de soins à risques infectieux et véhicules hors d'usage.   

Les déchets sont suivis de la production jusqu'au traitement final. Les déchets traités à l'étranger ne sont
pas tracés par Trackdéchets.
                """
                        ),
                    ],
                    width=12,
                )
            ]
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    [
                        html.Section(
                            [
                                html.H3(
                                    [
                                        html.Button(
                                            [
                                                html.Span(
                                                    className="fr-icon-info-fill",
                                                    **{"aria-hidden": "true"}
                                                ),
                                                "En savoir plus",
                                            ],
                                            className="fr-accordion__btn",
                                            **{
                                                "aria-expanded": "false",
                                                "aria-controls": "accordion-106",
                                            }
                                        )
                                    ],
                                    className="fr-accordion__title",
                                ),
                                html.Div(
                                    [
                                        dcc.Markdown(
                                            [
                                                """
Un borderau de suivi de déchet (BSD) est créé pour chaque déchet et il contient de nombreuses
informations (acteurs, déchets, poids, traitement réalisé, etc.). Ces informations sont transmises à
Trackdéchets par un usage direct ou par API.

Depuis le 1er janvier 2022, l'utilisation de Trackdéchets est obligatoire pour les déchets dangereux (DD)
et les déchets d'amiante (DA).

Le contenu de cette page, alimenté par des milliers de bordereaux, est amené à s'enrichir régulièrement
avec de nouvelles statistiques.                                    
                                    """
                                            ]
                                        )
                                    ],
                                    className="fr-collapse",
                                    id="accordion-106",
                                ),
                            ],
                            className="fr-accordion",
                        )
                    ],
                    width=12,
                )
            ]
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    [
                        html.H2("Déchets dangereux"),
                        dcc.Markdown(
                            [
                                """
Les nombres présentés ici incluent tous les types de déchets nécessitant un suivi particulier : **déchets dangereux** (DD), **déchets d'amiante** (DA), déchets de **fluide frigorigène** (FF) et **déchets d'activités de soins à risques infectieux** (DASRI).
        """
                            ]
                        ),
                    ],
                    width=12,
                )
            ],
        ),
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
        dbc.Row(
            [
                dbc.Col(
                    [
                        add_figure(
                            quantity_processed_weekly,
                            "bsdd_processed_weekly",
                            "Quantité de déchets dangereux traités par semaine",
                        )
                    ],
                    width=12,
                )
            ]
        ),
        html.Div(
            className="fr-tabs",
            children=[
                html.Ul(
                    [
                        html.Li(
                            [
                                html.Button(
                                    ["Déchets dangereux"],
                                    id="tabpanel-404",
                                    tabIndex="0",
                                    role="tab",
                                    className="fr-tabs__tab",
                                    title="Bordereaux de Suivi de Déchets Dangereux",
                                    **{
                                        "aria-selected": "true",
                                        "aria-controls": "tabpanel-404-panel",
                                    }
                                )
                            ],
                            role="presentation",
                        ),
                        html.Li(
                            [
                                html.Button(
                                    ["Amiante"],
                                    id="tabpanel-405",
                                    tabIndex="-1",
                                    role="tab",
                                    className="fr-tabs__tab",
                                    title="Bordereaux de Suivi de Déchets d'Amiante",
                                    **{
                                        "aria-selected": "false",
                                        "aria-controls": "tabpanel-405-panel",
                                    }
                                )
                            ],
                            role="presentation",
                        ),
                        html.Li(
                            [
                                html.Button(
                                    ["Fluides Frigo"],
                                    id="tabpanel-406",
                                    tabIndex="-1",
                                    role="tab",
                                    className="fr-tabs__tab",
                                    title="Bordereaux de Suivi de Fluides Frigorigènes",
                                    **{
                                        "aria-selected": "false",
                                        "aria-controls": "tabpanel-406-panel",
                                    }
                                )
                            ],
                            role="presentation",
                        ),
                        html.Li(
                            [
                                html.Button(
                                    ["Activités de Soins à Risques Infectieux"],
                                    id="tabpanel-407",
                                    tabIndex="-1",
                                    role="tab",
                                    className="fr-tabs__tab",
                                    title="Bordereaux de Suivi de Déchets d'Activités de Soins à Risques Infectieux",
                                    **{
                                        "aria-selected": "false",
                                        "aria-controls": "tabpanel-407-panel",
                                    }
                                ),
                            ],
                            role="presentation",
                        ),
                    ],
                    className="fr-tabs__list",
                    role="tablist",
                    **{
                        "aria-label": "Onglets pour sélectionner le graphique pour le type de bordereau voulu"
                    }
                ),
                html.Div(
                    [
                        html.H4(
                            [
                                "Nombre de Bordereaux de Suivi de Déchets Dangereux créés par semaine"
                            ]
                        ),
                        dcc.Graph(figure=bsdd_created_weekly),
                    ],
                    id="tabpanel-404-panel",
                    className="fr-tabs__panel fr-tabs__panel--selected",
                    role="tabpanel",
                    tabIndex="0",
                    **{"aria-labelledby": "tabpanel-404"}
                ),
                html.Div(
                    [
                        html.H4(
                            [
                                "Nombre de Bordereaux de Suivi de Déchets d'Amiante créés par semaine"
                            ]
                        ),
                        dcc.Graph(figure=bsda_created_weekly),
                    ],
                    id="tabpanel-405-panel",
                    className="fr-tabs__panel",
                    role="tabpanel",
                    tabIndex="0",
                    **{"aria-labelledby": "tabpanel-405"}
                ),
                html.Div(
                    [
                        html.H4(
                            [
                                "Nombre de Bordereaux de Suivi de Fluides Frigorigènes créés par semaine"
                            ]
                        ),
                        dcc.Graph(figure=bsff_created_weekly),
                    ],
                    id="tabpanel-406-panel",
                    className="fr-tabs__panel",
                    role="tabpanel",
                    tabIndex="0",
                    **{"aria-labelledby": "tabpanel-406"}
                ),
                html.Div(
                    [
                        html.H4(
                            [
                                "Nombre de Bordereaux de Suivi de Déchets d'Activités de Soins à Risques Infectieux créés par semaine"
                            ]
                        ),
                        dcc.Graph(figure=bsdasri_created_weekly),
                    ],
                    id="tabpanel-407-panel",
                    className="fr-tabs__panel",
                    role="tabpanel",
                    tabIndex="0",
                    **{"aria-labelledby": "tabpanel-407"}
                ),
            ],
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
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.Ul(
                                    [
                                        html.Li(
                                            [
                                                html.Button(
                                                    ["Utilisateurs"],
                                                    id="tabpanel-201",
                                                    tabIndex="0",
                                                    role="tab",
                                                    className="fr-tabs__tab",
                                                    title="Nombre d'utilisateurs inscrits par semaine",
                                                    **{
                                                        "aria-selected": "true",
                                                        "aria-controls": "tabpanel-201-panel",
                                                    }
                                                )
                                            ],
                                            role="presentation",
                                        ),
                                        html.Li(
                                            [
                                                html.Button(
                                                    ["Établissements"],
                                                    id="tabpanel-202",
                                                    tabIndex="-1",
                                                    role="tab",
                                                    className="fr-tabs__tab",
                                                    title="Nombre d'établissements inscrits par semaine",
                                                    **{
                                                        "aria-selected": "false",
                                                        "aria-controls": "tabpanel-202-panel",
                                                    }
                                                )
                                            ],
                                            role="presentation",
                                        ),
                                    ],
                                    className="fr-tabs__list",
                                    role="tablist",
                                    **{
                                        "aria-label": "Onglets pour sélectionner le graphique pour le type de bordereau voulu"
                                    }
                                ),
                                html.Div(
                                    [
                                        html.H4(
                                            [
                                                "Nombre de comptes utilisateurs créés par semaine"
                                            ]
                                        ),
                                        dcc.Graph(figure=user_created_weekly),
                                    ],
                                    id="tabpanel-201-panel",
                                    className="fr-tabs__panel fr-tabs__panel--selected",
                                    role="tabpanel",
                                    tabIndex="0",
                                    **{"aria-labelledby": "tabpanel-201"}
                                ),
                                html.Div(
                                    [
                                        html.H4(
                                            [
                                                "Nombre de compte d'établissements créés par semaine"
                                            ]
                                        ),
                                        dcc.Graph(figure=company_created_weekly),
                                    ],
                                    id="tabpanel-202-panel",
                                    className="fr-tabs__panel",
                                    role="tabpanel",
                                    tabIndex="0",
                                    **{"aria-labelledby": "tabpanel-202"}
                                ),
                            ],
                            className="fr-tabs",
                        )
                    ],
                    width=12,
                )
            ]
        ),
        dcc.Markdown(
            "Statistiques développées avec [Plotly Dash](https://dash.plotly.com/introduction) ("
            "[code source](https://github.com/MTES-MCT/trackdechets-public-stats/))",
            className="source-code",
        ),
    ]
    return container
