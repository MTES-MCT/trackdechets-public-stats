"""This module contains the functions that allows to create the dash layout elements for home page.
"""

from datetime import datetime

import plotly.graph_objects as go
import polars as pl
from dash import dcc, html

from src.data.data_processing import (
    get_quantities_by_naf,
    get_recovered_and_eliminated_quantity_processed_by_week_series,
    get_total_bs_created,
    get_total_quantity_processed,
    get_waste_quantity_processed_by_processing_code_df,
    get_weekly_aggregated_series,
    get_weekly_preprocessed_dfs,
    get_weekly_waste_quantity_processed_by_operation_code_df,
)
from src.data.datasets import (
    ALL_BORDEREAUX_DATA,
    BSDA_DATA,
    BSDASRI_DATA,
    BSDD_DATA,
    BSFF_DATA,
    COMPANY_DATA,
    NAF_NOMENCLATURE_DATA,
    USER_DATA,
)
from src.data.utils import get_data_date_interval_for_year
from src.pages.figures_factory import (
    create_quantity_processed_sunburst_figure,
    create_treemap_companies_figure,
    create_weekly_created_figure,
    create_weekly_quantity_processed_figure,
    create_weekly_scatter_figure,
)
from src.pages.utils import add_callout, add_figure

PLOTLY_PLOT_CONFIGS = {
    "toImageButtonOptions": {
        "format": "png",  # one of png, svg, jpeg, webp
        "filename": "trackdechets",
        "height": 1080,
        "width": 1920,
        "scale": 1,  # Multiply title/legend/axis/canvas sizes by this factor
    },
    "displaylogo": False,
    "locale": "fr",
}


def get_header_elements() -> html.Div:
    """It creates the header of the page, which contains the title, the last update date, a short
    description of Trackdéchets, three callout elements with the total number of bordereaux created, the total
    quantity of waste processed and the total number of companies created, and a navigation bar to
    select the year of the data to display.

    Returns
    -------
        A Div element containing the header of the page.

    """

    # Load all needed data
    company_data_df = COMPANY_DATA

    total_bs_created = get_total_bs_created(ALL_BORDEREAUX_DATA)

    total_quantity_processed = get_total_quantity_processed(ALL_BORDEREAUX_DATA)

    total_companies_created = company_data_df.height

    elements = [
        html.Div(
            [
                html.H1("Statistiques de Trackdéchets"),
                html.P(
                    [
                        f"Dernière mise à jour des données le {datetime.now().strftime('%d/%m/%Y')}"
                    ],
                    className="fr-badge fr-badge--info",
                    id="update-date",
                ),
                dcc.Markdown(
                    """
Cette page publique présente les données disponibles sur Trackdéchets.

Depuis le 1er janvier 2022, l'utilisation de Trackdéchets est obligatoire pour les déchets dangereux et/ou contenant des POP et les déchets d'amiante. 
Cependant, 2022 est une année de transition qui comprenait une période de tolérance jusqu'au 1er juillet (usage du format papier possible durant cette période). Nous utilisons donc les seules données qui ont fait l'objet d'une dématérialisation via Trackdéchets.
                """
                ),
            ]
        ),
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
                            },
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
            id="see-more-accordion",
        ),
        html.H2("Depuis 2020, Trackdéchets c'est...", id="callout-title"),
        html.Div(
            [
                add_callout(
                    number=total_quantity_processed,
                    text="tonnes de déchets dangereux* tracés et traités au total",
                ),
                add_callout(
                    number=total_bs_created,
                    text="bordereaux créés au total",
                ),
                add_callout(
                    number=total_companies_created,
                    text="établissements inscrits au total",
                ),
            ],
            className="row",
        ),
        html.Nav(
            get_navbar_elements([2022, 2023], 2022),
            className="fr-nav",
            id="header-navigation",
            role="navigation",
            **{"aria-label": "Menu de sélection de l'année des données à afficher"},
        ),
    ]

    return html.Div(elements, id="header-container")


def get_graph_elements_for_a_year(
    quantity_processed_total: int,
    bs_created_total: int,
    quantity_processed_weekly: go.Figure,
    quantity_processed_sunburst_figure: go.Figure,
    bsdd_counts_weekly: go.Figure,
    bsda_counts_weekly: go.Figure,
    bsff_counts_weekly: go.Figure,
    bsdasri_counts_weekly: go.Figure,
    bsdd_quantities_weekly: go.Figure,
    bsda_quantities_weekly: go.Figure,
    bsdasri_quantities_weekly: go.Figure,
    produced_quantity_by_category: go.Figure,
    company_created_total_life: int,
    user_created_total_life: int,
    company_created_weekly: go.Figure,
    user_created_weekly: go.Figure,
    company_counts_by_category: go.Figure,
    year: int,
) -> list:
    """
    Creates the div container that contains all the graphes and that will be displayed using all the precomputed metrics and Plotly Figures objects.

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
    bsdd_counts_weekly: Plotly Figure object
        Scatter plot showing the number of BSDD weekly created, sent, received and processed.
    bsda_counts_weekly: Plotly Figure object
        Scatter plot showing the number of BSDA weekly created, sent, received and processed.
    bsff_counts_weekly: Plotly Figure object
        Scatter plot showing the number of BSFF weekly created, sent, received and processed.
    bsdasri_counts_weekly: Plotly Figure object
        Scatter plot showing the number of BSDASRI weekly created, sent, received and processed.
    bsdd_quantities_weekly: Plotly Figure object
        Scatter plot showing the waste weekly quantities created, sent, received and processed.
    bsda_quantities_weekly: Plotly Figure object
        Scatter plot showing the waste weekly quantities created, sent, received and processed.
    bsff_quantities_weekly: Plotly Figure object
        Scatter plot showing the waste weekly quantities created, sent, received and processed.
    bsdasri_quantities_weekly: Plotly Figure object
        Scatter plot showing the waste weekly quantities created, sent, received and processed.
    company_created_total_life: int
        Number of companies with an account on the Trackdéchets platform (all time).
    user_created_total_life: int
        Number of users with an account on the Trackdéchets platform (all time).
    company_created_weekly: Plotly Figure object
        Scatter plot showing the number of company accounts created weekly.
    user_created_weekly: Plotly Figure object
        Scatter plot showing the number of user accounts created weekly.
    year: int
        The year for which the data is displayed.

    Returns
    -------
    list
        Layout as a list of Dash components, ready to be rendered.
    """

    elements = [
        html.H3(f"Statistiques pour l'année {year}", id="stats-year-title"),
        html.Div(
            [
                add_callout(
                    number=quantity_processed_total,
                    text=f"tonnes de déchets dangereux* tracés et traités sur l'année {year}",
                ),
                add_callout(
                    number=bs_created_total,
                    text=f"bordereaux créés sur l'année {year}",
                ),
                dcc.Markdown(
                    """Les modes de traitement des déchets dangereux s'inscrivent dans la [hiérarchie des traitements de déchets](https://www.ecologie.gouv.fr/gestion-des-dechets-principes-generaux#scroll-nav__4).
Ainsi la réutilisation, le recyclage ou la valorisation sont considérés comme "valorisés" dans Trackdéchets, et sont comparés à l'élimination (pas de réutilisation, recyclage ou valorisation possible dans les conditions techniques et économiques du moment).""",
                    id="processing-explanation-block",
                    className="fr-callout",
                ),
            ],
            className="row",
        ),
        html.Div(
            [
                add_figure(
                    quantity_processed_weekly,
                    "bsdd_processed_weekly",
                    "Quantité de déchets dangereux* tracés et traités par semaine",
                )
            ]
        ),
        html.Div(
            [
                add_figure(
                    quantity_processed_sunburst_figure,
                    "bsdd_processed_by_operation",
                    "Quantité de déchets dangereux* tracés et traités par opération de traitement",
                    (
                        "Le cœur du graphique représente la part de déchets valorisés et éliminés, "
                        "les sections autour permettent d'avoir une idée de la part de déchets par type d'opération de traitement."
                    ),
                ),
                add_callout(
                    text="""Les codes R (recovery, valorisation) et D (disposal, élimination) définis par la convention de Bâle, et repris aux annexes I et II de la directive cadre déchets n° 2008/98/CE, sont régulièrement exploités dans le contexte de la traçabilité des déchets et de la déclaration annuelle des émissions et des transferts de polluants et des déchets (déclaration GEREP). Ces codes permettent de discerner les différentes opérations de valorisation et d’élimination des déchets. La liste des codes déchets peut être retrouvées en annexe de la [notice BSDD](https://faq.trackdechets.fr/dechets-dangereux-classiques/telecharger-la-notice-et-le-recepisse-du-bsdd).""",
                ),
            ],
            className="row",
            id="operation-type-section",
        ),
        html.Div(
            "*tous déchets dangereux et/ou POP (Polluants Organiques Persistants)",
            className="fr-text--xs",
        ),
        html.H4(["Détail par types de déchets dangereux"]),
        html.Div(
            "Astuce : vous pouvez cliquer sur les textes de la légende pour faire disparaître ou apparaître les différentes courbes.",
            className="fr-text--sm tips-container",
        ),
        html.Div(
            html.Div(
                className="fr-tabs",
                children=[
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Button(
                                        ['Déchets dangereux "classiques"'],
                                        id="tabpanel-404",
                                        tabIndex="0",
                                        role="tab",
                                        className="fr-tabs__tab",
                                        title="Bordereaux de Suivi de Déchets Dangereux",
                                        **{
                                            "aria-selected": "true",
                                            "aria-controls": "tabpanel-404-panel",
                                        },
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
                                        },
                                    )
                                ],
                                role="presentation",
                            ),
                            html.Li(
                                [
                                    html.Button(
                                        ["Fluides Frigorigènes"],
                                        id="tabpanel-406",
                                        tabIndex="-1",
                                        role="tab",
                                        className="fr-tabs__tab",
                                        title="Bordereaux de Suivi de Fluides Frigorigènes",
                                        **{
                                            "aria-selected": "false",
                                            "aria-controls": "tabpanel-406-panel",
                                        },
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
                                        },
                                    ),
                                ],
                                role="presentation",
                            ),
                        ],
                        className="fr-tabs__list",
                        role="tablist",
                        **{
                            "aria-label": "Onglets pour sélectionner le graphique pour le type de bordereau voulu"
                        },
                    ),
                    html.Div(
                        [
                            html.H4(
                                [
                                    "Nombre de Bordereaux de Suivi de Déchets Dangereux par semaine"
                                ]
                            ),
                            dcc.Graph(
                                figure=bsdd_counts_weekly,
                                config=PLOTLY_PLOT_CONFIGS,
                                id={
                                    "type": "counts-figure",
                                    "index": "bsdd",
                                    "year": year,
                                },
                            ),
                            html.H4(
                                ["Quantités de Déchets Dangereux tracés par semaine"]
                            ),
                            dcc.Graph(
                                figure=bsdd_quantities_weekly,
                                config=PLOTLY_PLOT_CONFIGS,
                                id={
                                    "type": "counts-figure",
                                    "index": "bsdd-quantities",
                                    "year": year,
                                },
                            ),
                        ],
                        id="tabpanel-404-panel",
                        className="fr-tabs__panel fr-tabs__panel--selected",
                        role="tabpanel",
                        tabIndex="0",
                        **{"aria-labelledby": "tabpanel-404"},
                    ),
                    html.Div(
                        [
                            html.H4(
                                [
                                    "Nombre de Bordereaux de Suivi de Déchets d'Amiante par semaine"
                                ]
                            ),
                            dcc.Graph(
                                figure=bsda_counts_weekly,
                                config=PLOTLY_PLOT_CONFIGS,
                                id={
                                    "type": "counts-figure",
                                    "index": "bsda",
                                    "year": year,
                                },
                            ),
                            html.H4(
                                ["Quantités de Déchets D'amiante tracés par semaine"]
                            ),
                            dcc.Graph(
                                figure=bsda_quantities_weekly,
                                config=PLOTLY_PLOT_CONFIGS,
                                id={
                                    "type": "counts-figure",
                                    "index": "bsda-quantities",
                                    "year": year,
                                },
                            ),
                        ],
                        id="tabpanel-405-panel",
                        className="fr-tabs__panel",
                        role="tabpanel",
                        tabIndex="0",
                        **{"aria-labelledby": "tabpanel-405"},
                    ),
                    html.Div(
                        [
                            html.Div(
                                "Éléments à titre indicatif, la traçabilité est obligatoire à compter du 1 avril 2023.",
                                className="fr-text--sm",
                            ),
                            html.H4(
                                [
                                    "Nombre de Bordereaux de Suivi de Fluides Frigorigènes par semaine"
                                ]
                            ),
                            dcc.Graph(
                                figure=bsff_counts_weekly,
                                config=PLOTLY_PLOT_CONFIGS,
                                id={
                                    "type": "counts-figure",
                                    "index": "bsff",
                                    "year": year,
                                },
                            ),
                        ],
                        id="tabpanel-406-panel",
                        className="fr-tabs__panel",
                        role="tabpanel",
                        tabIndex="0",
                        **{"aria-labelledby": "tabpanel-406"},
                    ),
                    html.Div(
                        [
                            html.Div(
                                "Éléments à titre indicatif, la dématérialisation n'étant pas encore réglementée, les exutoires ne sont pas tous prêts.",
                                className="fr-text--sm",
                            ),
                            html.H4(
                                [
                                    "Nombre de Bordereaux de Suivi de Déchets d'Activités de Soins à Risques Infectieux par semaine"
                                ]
                            ),
                            dcc.Graph(
                                figure=bsdasri_counts_weekly,
                                config=PLOTLY_PLOT_CONFIGS,
                                id={
                                    "type": "counts-figure",
                                    "index": "bsdasri",
                                    "year": year,
                                },
                            ),
                            html.H4(
                                [
                                    "Quantités de Déchets d'Activités de Soins à Risques Infectieux tracés par semaine"
                                ]
                            ),
                            dcc.Graph(
                                figure=bsdasri_quantities_weekly,
                                config=PLOTLY_PLOT_CONFIGS,
                                id={
                                    "type": "counts-figure",
                                    "index": "bsdasri-quantities",
                                    "year": year,
                                },
                            ),
                        ],
                        id="tabpanel-407-panel",
                        className="fr-tabs__panel",
                        role="tabpanel",
                        tabIndex="0",
                        **{"aria-labelledby": "tabpanel-407"},
                    ),
                ],
            ),
            id="bordereaux-counts-section",
        ),
        html.Div(
            [
                add_figure(
                    produced_quantity_by_category,
                    "produced_quantity_by_category",
                    "Quels sont les catégories d'entreprises qui produisent le plus de déchets dangereux* ?",
                    (
                        "La Nomenclature des Activités Françaises permet de catégoriser "
                        "les différents établissements qui produisent des déchets tracés sur Trackdéchets."
                        "Les établissements qui reçoivent des déchets ont été exclus pour "
                        "être certain de ne pas prendre en compte les établissements faisant du Tri, Transit, Regroupement (TTR)."
                        "</br>Un clic sur une des catégories permet de visualiser la hiérarchie suivante."
                    ),
                )
            ]
        ),
        html.H4("Établissements et utilisateurs"),
        html.Div(
            [
                add_callout(
                    number=company_created_total_life,
                    text=f"établissements inscrits sur l'année {year}"
                    if year == 2022
                    else f"nouveaux établissements inscrits sur l'année {year}",
                ),
                add_callout(
                    number=user_created_total_life,
                    text=f"utilisateurs inscrits sur l'année {year}"
                    if year == 2022
                    else f"nouveaux utilisateurs inscrits sur l'année {year}",
                ),
            ],
            className="row",
            id="companies-users-total-section",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Ul(
                            [
                                html.Li(
                                    [
                                        html.Button(
                                            ["Établissements"],
                                            id="tabpanel-202",
                                            tabIndex="0",
                                            role="tab",
                                            className="fr-tabs__tab",
                                            title="Nombre d'établissements inscrits par semaine",
                                            **{
                                                "aria-selected": "true",
                                                "aria-controls": "tabpanel-201-panel",
                                            },
                                        )
                                    ],
                                    role="presentation",
                                ),
                                html.Li(
                                    [
                                        html.Button(
                                            ["Utilisateurs"],
                                            id="tabpanel-201",
                                            tabIndex="-1",
                                            role="tab",
                                            className="fr-tabs__tab",
                                            title="Nombre d'utilisateurs inscrits par semaine",
                                            **{
                                                "aria-selected": "false",
                                                "aria-controls": "tabpanel-202-panel",
                                            },
                                        )
                                    ],
                                    role="presentation",
                                ),
                            ],
                            className="fr-tabs__list",
                            role="tablist",
                            **{
                                "aria-label": "Onglets pour sélectionner le graphique pour le type de bordereau voulu"
                            },
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
                            id="tabpanel-201-panel",
                            className="fr-tabs__panel fr-tabs__panel--selected",
                            role="tabpanel",
                            tabIndex="0",
                            **{"aria-labelledby": "tabpanel-201"},
                        ),
                        html.Div(
                            [
                                html.H4(
                                    ["Nombre de comptes utilisateurs créés par semaine"]
                                ),
                                dcc.Graph(
                                    figure=user_created_weekly,
                                    config=PLOTLY_PLOT_CONFIGS,
                                ),
                            ],
                            id="tabpanel-202-panel",
                            className="fr-tabs__panel",
                            role="tabpanel",
                            tabIndex="0",
                            **{"aria-labelledby": "tabpanel-202"},
                        ),
                    ],
                    className="fr-tabs",
                )
            ],
            id="companies-users-counts-section",
        ),
        html.Div(
            [
                add_figure(
                    company_counts_by_category,
                    "company_counts_by_category",
                    "Nombre d'entreprises inscrites pour chaque catégorie de code NAF",
                    (
                        "La Nomenclature des Activités Françaises permet de catégoriser "
                        "les différents établissements qui s'inscrivent sur Trackdéchets."
                        " Un clic sur une des catégories permet de visualiser la hiérarchie suivante."
                    ),
                )
            ]
        ),
        html.Div(
            dcc.Markdown(
                "Application de visualisation de données statistiques développée avec [Plotly Dash](https://dash.plotly.com/introduction) ("
                "[code source](https://github.com/MTES-MCT/trackdechets-public-stats/))",
                className="source-code",
            )
        ),
    ]
    return elements


def get_navbar_elements(years: list[int], year_selected: int) -> html.Ul:
    """
    Creates the navbar elements needed for the home page menu that allows
    to select the year for which the data is displayed.

    Parameters
    ----------
    years: List of ints
        The list of years to add as button in the navbar menu.
    year_selected: int
        The year that is in the 'selected' state.

    Returns
    -------
    A Dash Ul element containing the navbar menu elements.
    """

    elements = []

    for year in years:
        if year_selected == year:
            link_element = html.Span(
                f"Année {year}",
                className="fr-nav__link",
                id={"type": "year-selector", "index": year},
                **{"aria-current": "page"},
            )
        else:
            link_element = html.Span(
                f"Année {year}",
                className="fr-nav__link",
                id={"type": "year-selector", "index": year},
            )

        elements.append(
            html.Li(
                link_element,
                className="fr-nav__item",
            )
        )

    return html.Ul(
        elements, className="fr-nav__list", id="header-nav-elements-container"
    )


def get_layout_for_a_year(year: int = 2022) -> list:
    """
    Creates the layout that contains all the graph elements for a particular year of data.

    Returns
    -------
    list
        A list of dash elements to be inserted in the Div with id 'graph-container'.
    """

    date_interval = get_data_date_interval_for_year(year)

    # Load all needed data
    bsdd_data_df = BSDD_DATA
    bsda_data_df = BSDA_DATA
    bsff_data_df = BSFF_DATA
    bsdasri_data_df = BSDASRI_DATA

    # BSx weekly figures
    bsdd_weekly_processed_dfs = get_weekly_preprocessed_dfs(bsdd_data_df, date_interval)
    bsda_weekly_processed_dfs = get_weekly_preprocessed_dfs(bsda_data_df, date_interval)
    bsff_weekly_processed_dfs = get_weekly_preprocessed_dfs(bsff_data_df, date_interval)
    bsdasri_weekly_processed_dfs = get_weekly_preprocessed_dfs(
        bsdasri_data_df, date_interval
    )

    lines_configs = [
        {
            "name": "État initial",
            "suffix": "traçés",
            "text_position": "top center",
        },
        {
            "name": "Pris en charge par le transporteur",
            "suffix": "pris en charge par le transporteur",
            "text_position": "middle top",
        },
        {
            "name": "Reçu par le destinataire",
            "suffix": "reçus par le destinataire",
            "text_position": "middle bottom",
        },
        {
            "name": "Traité",
            "suffix": "marqués comme traités",
            "text_position": "bottom center",
        },
        {
            "name": "Traité (traitement intermédiaire)",
            "suffix": "en traitement intermédiaire",
            "text_position": "bottom center",
        },
        {
            "name": "Traité (traitement final)",
            "suffix": "en traitement final",
            "text_position": "bottom center",
        },
    ]
    bsdd_counts_weekly_fig = create_weekly_scatter_figure(
        *bsdd_weekly_processed_dfs["counts"],
        bs_type="BSDD",
        lines_configs=lines_configs,
    )
    bsda_counts_weekly_fig = create_weekly_scatter_figure(
        *bsda_weekly_processed_dfs["counts"],
        bs_type="BSDA",
        lines_configs=lines_configs,
    )
    bsff_counts_weekly_fig = create_weekly_scatter_figure(
        *bsff_weekly_processed_dfs["counts"],
        bs_type="BSFF",
        lines_configs=lines_configs,
    )
    bsdasri_counts_weekly_fig = create_weekly_scatter_figure(
        *bsdasri_weekly_processed_dfs["counts"],
        bs_type="BSDASRI",
        lines_configs=lines_configs,
    )

    lines_configs = [
        {
            "name": "Quantité initiale",
            "suffix": "tonnes tracées",
            "text_position": "top center",
        },
        {
            "name": "Prise en charge par le transporteur",
            "suffix": "tonnes prises en charge par le transporteur",
            "text_position": "middle top",
        },
        {
            "name": "Reçue par le destinataire",
            "suffix": "tonnes reçues par le destinataire",
            "text_position": "middle bottom",
        },
        {
            "name": "Traitée",
            "suffix": "tonnes traitées",
            "text_position": "bottom center",
        },
        {
            "name": "Traitée (traitement intermédiaire)",
            "suffix": "tonnes traitées en traitement intermédiaire",
            "text_position": "bottom center",
        },
        {
            "name": "Traitée (traitement final)",
            "suffix": "tonnes traitées en traitement final",
            "text_position": "bottom center",
        },
    ]
    bsdd_quantities_weekly_fig = create_weekly_scatter_figure(
        *bsdd_weekly_processed_dfs["quantity"],
        bs_type="BSDD",
        lines_configs=lines_configs,
    )
    bsda_quantities_weekly_fig = create_weekly_scatter_figure(
        *bsda_weekly_processed_dfs["quantity"],
        bs_type="BSDA",
        lines_configs=lines_configs,
    )
    bsdasri_quantities_weekly_fig = create_weekly_scatter_figure(
        *bsdasri_weekly_processed_dfs["quantity"],
        bs_type="BSDASRI",
        lines_configs=lines_configs,
    )

    # Waste weight processed weekly
    quantity_processed_weekly_df = (
        get_weekly_waste_quantity_processed_by_operation_code_df(
            ALL_BORDEREAUX_DATA, date_interval
        )
    )

    # Total bordereaux created
    bs_created_total = get_total_bs_created(ALL_BORDEREAUX_DATA, date_interval)

    # Waste weight processed weekly
    (
        recovered_quantity_series,
        eliminated_quantity_series,
    ) = get_recovered_and_eliminated_quantity_processed_by_week_series(
        quantity_processed_weekly_df
    )
    quantity_processed_weekly_fig = create_weekly_quantity_processed_figure(
        recovered_quantity_series, eliminated_quantity_series
    )

    waste_quantity_processed_by_processing_code_df = (
        get_waste_quantity_processed_by_processing_code_df(quantity_processed_weekly_df)
    )

    quantity_processed_sunburst_fig = create_quantity_processed_sunburst_figure(
        waste_quantity_processed_by_processing_code_df
    )

    quantity_processed_total = get_total_quantity_processed(
        ALL_BORDEREAUX_DATA, date_interval
    )

    # Company and user section
    company_data_df = COMPANY_DATA.filter(
        pl.col("created_at").is_between(*date_interval, closed="left")
    )
    user_data_df = USER_DATA.filter(
        pl.col("created_at").is_between(*date_interval, closed="left")
    )

    company_created_total_life = company_data_df.height
    user_created_total_life = user_data_df.height

    company_created_weekly_df = get_weekly_aggregated_series(company_data_df)
    user_created_weekly_df = get_weekly_aggregated_series(user_data_df)

    company_created_weekly = create_weekly_created_figure(company_created_weekly_df)
    user_created_weekly = create_weekly_created_figure(user_created_weekly_df)

    treemap_companies_figure = create_treemap_companies_figure(company_data_df)

    all_bordereaux_with_naf = get_quantities_by_naf(
        ALL_BORDEREAUX_DATA, NAF_NOMENCLATURE_DATA, date_interval
    )

    produced_quantity_by_category = create_treemap_companies_figure(
        all_bordereaux_with_naf, use_quantity=True
    )

    # generate
    elements = get_graph_elements_for_a_year(
        quantity_processed_total=quantity_processed_total,
        bs_created_total=bs_created_total,
        quantity_processed_weekly=quantity_processed_weekly_fig,
        quantity_processed_sunburst_figure=quantity_processed_sunburst_fig,
        bsdd_counts_weekly=bsdd_counts_weekly_fig,
        bsda_counts_weekly=bsda_counts_weekly_fig,
        bsff_counts_weekly=bsff_counts_weekly_fig,
        bsdasri_counts_weekly=bsdasri_counts_weekly_fig,
        bsdd_quantities_weekly=bsdd_quantities_weekly_fig,
        bsda_quantities_weekly=bsda_quantities_weekly_fig,
        bsdasri_quantities_weekly=bsdasri_quantities_weekly_fig,
        produced_quantity_by_category=produced_quantity_by_category,
        company_created_total_life=company_created_total_life,
        user_created_total_life=user_created_total_life,
        company_created_weekly=company_created_weekly,
        user_created_weekly=user_created_weekly,
        company_counts_by_category=treemap_companies_figure,
        year=year,
    )

    return elements
