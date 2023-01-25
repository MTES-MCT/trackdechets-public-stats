"""This module is where the home page is registered and its initial layout rendered.
"""
from datetime import datetime
from dash import html, register_page, dcc


from src.pages.home.home_layouts import layout_2022
from src.pages.home.home_layout_factory import get_navbar_elements

register_page(
    __name__,
    path="/",
    description="Page d'accueil des statistiques publiques de la plateforme Trackdéchets.",
    name="Accueil - Statistiques Publiques de Trackdéchets",
)


def layout() -> html.Div:
    """
    Creates initial layout. Currently the initial layout displays 2022 data.

    Returns
    -------
    A Dash Div with the id 'main-container'.
    """

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
        html.Nav(
            get_navbar_elements([2022, 2023], 2022),
            className="fr-nav",
            id="header-navigation",
            role="navigation",
            **{"aria-label": "Menu de sélection de l'année des données à afficher"},
        ),
        dcc.Loading(
            html.Div(
                layout_2022,
                id="graph-container",
            ),
            style={"position": "absolute", "top": "25px"},
            color="rgb(0, 0, 145)",
            type="circle",
        ),
    ]

    return html.Div(elements, id="main-container")
