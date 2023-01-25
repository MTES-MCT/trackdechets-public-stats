from dash import html, register_page, dcc

from src.data.data_extract import (
    get_departement_geographical_data,
    get_waste_nomenclature_data,
)


def create_selects():

    geographical_data = get_departement_geographical_data()
    waste_nomenclature = get_waste_nomenclature_data()

    options = (
        geographical_data[["code_departement", "libelle"]]
        .rename(columns={"code_departement": "value", "libelle": "label"})
        .to_dict(orient="records")
    )

    departements_dropdown = html.Div(
        [
            html.Label(
                ["Sélectionner un département :"],
                className="fr-label",
                htmlFor="departement-select",
            ),
            dcc.Dropdown(
                options=options,
                placeholder="Rechercher un département...",
                id="departement-select",
            ),
        ],
        className="fr-select-group",
    )

    waste_nomenclature["description"] = (
        waste_nomenclature["code"] + " - " + waste_nomenclature["description"]
    )
    options = waste_nomenclature.rename(
        columns={"code": "value", "description": "label"}
    ).to_dict(orient="records")

    waste_dropdown = html.Div(
        [
            html.Label(
                ["Sélectionner un ou plusieurs code déchets :"],
                className="fr-label",
                htmlFor="waste-select",
            ),
            dcc.Dropdown(
                options=options,
                placeholder="Rechercher un code déchet...",
                id="waste-select",
            ),
        ],
        className="fr-select-group",
    )

    selects_div = html.Div(
        [departements_dropdown, waste_dropdown], className="selects-container"
    )

    return selects_div
