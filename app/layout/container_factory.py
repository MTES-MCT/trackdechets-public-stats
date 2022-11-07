import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from app.layout.utils import add_callout, add_figure
from dash import dcc, html

PLOTLY_PLOT_CONFIGS = {
    "toImageButtonOptions": {
        "format": "png",  # one of png, svg, jpeg, webp
        "filename": "trackdechets",
        "height": 720,
        "width": 1280,
        "scale": 1,  # Multiply title/legend/axis/canvas sizes by this factor
    },
    "displaylogo": False,
}


def create_public_stats_container(
    quantity_processed_total: int,
    bs_created_total: int,
    quantity_processed_weekly: go.Figure,
    quantity_processed_sunburst_figure: go.Figure,
    bsdd_created_weekly: go.Figure,
    bsda_created_weekly: go.Figure,
    bsff_created_weekly: go.Figure,
    bsdasri_created_weekly: go.Figure,
    company_created_total_life: int,
    user_created_total_life: int,
    company_created_weekly: go.Figure,
    user_created_weekly: go.Figure,
) -> list:
    """
    Creates the main container that will be displayed using all the precomputed metrics and Plotly Figures objects.
    Currently data is supposed to be for the year 2022.

    Parameters
    ----------
    quantity_processed_total: int
        Number of tons of waste processed.
    bsdd_created_total: int
        Total number of bordereaux created (BSDD, BSDA, BSFF and BSDASRI).
    quantity_processed_weekly: Plotly Figure object
        Bar plot showing the quantity of waste processed by week and by process type.
    quantity_processed_sunburst_figure: Plotly Figure object
        Sunburst plot showing the waste quantity by processing code.
    bsdd_created_weekly: Plotly Figure object
        Scatter plot showing the number of BSDD created weekly.
    bsda_created_weekly: Plotly Figure object
        Scatter plot showing the number of BSDA created weekly.
    bsff_created_weekly: Plotly Figure object
        Scatter plot showing the number of BSFF created weekly.
    bsdasri_created_weekly: Plotly Figure object
        Scatter plot showing the number of BSDASRI created weekly.
    company_created_total_life: int
        Number of companies with an account on the Trackdéchets platform (all time).
    user_created_total_life: int
        Number of users with an account on the Trackdéchets platform (all time).
    company_created_weekly: Plotly Figure object
        Scatter plot showing the number of company accounts created weekly.
    user_created_weekly: Plotly Figure object
        Scatter plot showing the number of user accounts created weekly.

    Returns
    -------
    list
        Layout as a list of Dash components, ready to be rendered.
    """
    container = [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1("Statistiques de Trackdéchets"),
                        dcc.Markdown(
                            """
Cette page publique, est le reflet des données disponibles sur Trackdéchets.

Depuis le 1er janvier 2022, l'utilisation de Trackdéchets est obligatoire pour les déchets dangereux et les déchets d'amiante. Cependant, 2022  est une année de transition qui comprend une période de tolérance jusqu'au 1er juillet (usage du format papier possible durant cette période).
Nous utilisons donc les seules données qui ont fait l'objet d'une dématérialisation via Trackdéchets.
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
L'application Trackdéchets est utilisée en France pour tracer plusieurs types de déchets:
- déchets dangereux et/ou contenant des Polluants Organiques Persistants ([POP](https://www.ecologie.gouv.fr/polluants-organiques-persistants-pop)) ;
- déchets contenant de l'amiante ;
- déchets de fluides frigorigènes ;
- déchets d'activités de soins à risques infectieux (DASRI) ;
- véhicules hors d'usage.

Les déchets doivent être tracés depuis le producteur/détenteur jusqu'au traitement final.
Les déchets qui vont d'une installation en métropole, à destination de l'étranger (ou l'inverse) ne sont pas tracés par Trackdéchets.
Un bordereau de suivi de déchet (BSD) est créé pour chaque déchet et chaque mouvement. Les nombreuses informations qu'il contient alimentent ces statistiques.                   
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
Les données présentées ici comprennent tous les types de déchets nécessitant un suivi particulier : **déchets dangereux** (DD), **déchets d'amiante** (DA), déchets de **fluide frigorigène** (FF) et **déchets d'activités de soins à risques infectieux** (DASRI).        
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
                    sm_width=12,
                ),
                add_callout(
                    number=bs_created_total,
                    text="bordereaux créés sur depuis le 1er janvier 2022",
                    width=3,
                    sm_width=12,
                ),
                add_callout(
                    text="""Les modes de traitement des déchets dangereux s'inscrivent dans la [hiérarchie des traitements de déchets](https://www.ecologie.gouv.fr/gestion-des-dechets-principes-generaux#:~:text=La%20hi%C3%A9rarchie%20des%20modes%20de%20traitement%20est%20un%20ordre%20de,d%C3%A9marches%20de%20pr%C3%A9vention%20des%20d%C3%A9chets).
Ainsi la réutilisation, le recyclage ou la valorisation sont considérés comme "valorisés" dans Trackdéchets, et sont comparés à l'élimination (pas de réutilisation, recyclage ou valorisation possible dans les conditions techniques et économiques du moment)""",
                    width=6,
                    sm_width=12,
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
        dbc.Row(
            [
                dbc.Col(
                    [
                        add_figure(
                            quantity_processed_sunburst_figure,
                            "bsdd_processed_by_operation",
                            "Quantité de déchets traités par opération de traitement",
                        )
                    ],
                    width=8,
                ),
                add_callout(
                    text="""Les codes R (recovery, valorisation) et D (disposal, élimination) définis par la convention de Bâle, et repris aux annexes I et II de la directive cadre déchets n° 2008/98/CE, sont régulièrement exploités dans le contexte de la traçabilité des déchets et de la déclaration annuelle des émissions et des transferts de polluants et des déchets (déclaration GEREP). Ces codes permettent de discerner les différentes opérations de valorisation et d’élimination des déchets. La liste des codes déchets peut être retrouvées en annexe de la [notice BSDD](https://faq.trackdechets.fr/dechets-dangereux-classiques/telecharger-la-notice-et-le-recepisse-du-bsdd).""",
                    width=4,
                    sm_width=12,
                ),
            ]
        ),
        dbc.Row(
            dbc.Col(
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
                                    role="present_ation",
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
                                    role="present_ation",
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
                                    role="present_ation",
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
                                    role="present_ation",
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
                                        "Nombre de Bordereaux de Suivi de Déchets Dangereux par semaine"
                                    ]
                                ),
                                dcc.Graph(
                                    figure=bsdd_created_weekly,
                                    config=PLOTLY_PLOT_CONFIGS,
                                ),
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
                                        "Nombre de Bordereaux de Suivi de Déchets d'Amiante par semaine"
                                    ]
                                ),
                                dcc.Graph(
                                    figure=bsda_created_weekly,
                                    config=PLOTLY_PLOT_CONFIGS,
                                ),
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
                                        "Nombre de Bordereaux de Suivi de Fluides Frigorigènes par semaine"
                                    ]
                                ),
                                dcc.Graph(
                                    figure=bsff_created_weekly,
                                    config=PLOTLY_PLOT_CONFIGS,
                                ),
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
                                        "Nombre de Bordereaux de Suivi de Déchets d'Activités de Soins à Risques Infectieux par semaine"
                                    ]
                                ),
                                dcc.Graph(
                                    figure=bsdasri_created_weekly,
                                    config=PLOTLY_PLOT_CONFIGS,
                                ),
                            ],
                            id="tabpanel-407-panel",
                            className="fr-tabs__panel",
                            role="tabpanel",
                            tabIndex="0",
                            **{"aria-labelledby": "tabpanel-407"}
                        ),
                    ],
                ),
                width=12,
            )
        ),
        dbc.Row(
            [
                html.H2("Établissements et utilisateurs"),
                add_callout(
                    number=company_created_total_life,
                    text="établissements inscrits au total",
                    width=3,
                    sm_width=12,
                ),
                add_callout(
                    number=user_created_total_life,
                    text="utilisateurs inscrits au total",
                    width=3,
                    sm_width=12,
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
                                            role="present_ation",
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
                                            role="present_ation",
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
                                        dcc.Graph(
                                            figure=user_created_weekly,
                                            config=PLOTLY_PLOT_CONFIGS,
                                        ),
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
                                        dcc.Graph(
                                            figure=company_created_weekly,
                                            config=PLOTLY_PLOT_CONFIGS,
                                        ),
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
        dbc.Row(
            dbc.Col(
                dcc.Markdown(
                    "Statistiques développées avec [Plotly Dash](https://dash.plotly.com/introduction) ("
                    "[code source](https://github.com/MTES-MCT/trackdechets-public-stats/))",
                    className="source-code",
                ),
                width=12,
            )
        ),
    ]
    return container
