from datetime import timedelta
from typing import Dict, List

import pandas as pd
import plotly.graph_objects as go

from src.pages.utils import break_long_line, format_number


def create_weekly_created_figure(
    data: pd.DataFrame,
) -> go.Figure:
    """Creates the figure showing number of weekly created Bsx, companies, users...

    Parameters
    ----------
    data: DataFrame
        DataFrame containing the data to plot. Must have 'id' and 'at' columns.

    Returns
    -------
    Plotly Figure Object
        Figure object ready to be plotted.
    """

    text_positions = [
        "top center" if i % 2 else "bottom center" for i in range(data.shape[0])
    ]

    texts = [
        f"Semaine du {e[0]-timedelta(days=6):%d/%m} au {e[0]:%d/%m}<br><b>{format_number(e[1])}</b> créations"
        for e in data.itertuples(index=False)
    ]

    fig = go.Figure(
        [
            go.Scatter(
                x=data["at"],
                y=data["count"],
                text=data["count"],
                mode="lines+markers+text",
                hovertext=texts,
                hoverinfo="text",
                textposition=text_positions,
            )
        ]
    )

    fig.update_layout(
        xaxis_title="Semaine de création",
        showlegend=False,
        paper_bgcolor="#fff",
        margin=dict(t=20, r=0, l=50),
    )
    fig.update_xaxes(tick0="2022-01-03")

    return fig


def create_weekly_scatter_figure(
    bs_created_data: pd.DataFrame,
    bs_sent_data: pd.DataFrame,
    bs_received_data: pd.DataFrame,
    bs_processed_non_final_data: pd.DataFrame,
    bs_processed_data: pd.DataFrame,
    lines_configs: List[Dict[str, str]],
) -> go.Figure:
    """Creates a scatter figure showing the weekly number of 'bordereaux' by status (created, sent..)

    Parameters
    ----------
    bs_created_data: DataFrame
        DataFrame containing the count of 'bordereaux' created. Must have 'at' and metric corresponding columns.
    bs_sent_data: DataFrame
        DataFrame containing the count of 'bordereaux' sent. Must have 'at' and metric corresponding columns.
    bs_received_data: DataFrame
        DataFrame containing the count of 'bordereaux' received. Must have 'at' and metric corresponding columns.
    bs_processed_non_final_data: DataFrame
        DataFrame containing the count of 'bordereaux' processed with non final processing operation code.
        Must have 'at' and metric corresponding columns.
    bs_processed_data: DataFrame
        DataFrame containing the count of 'bordereaux' processed with final processing operation code.
        Must have 'at' and metric corresponding columns.

    Returns
    -------
    Plotly Figure Object
        Figure object ready to be plotted.
    """

    # Those colors are colorblind safe and printable.
    # Source : https://personal.sron.nl/~pault/#sec:qualitative

    plot_configs = [
        {"data": bs_created_data, **lines_configs[0]},
        {"data": bs_sent_data, **lines_configs[1]},
        {"data": bs_received_data, **lines_configs[2]},
        {
            "data": bs_processed_non_final_data,
            **lines_configs[3],
        },
        {"data": bs_processed_data, **lines_configs[4]},
    ]

    scatter_list = []

    metric_name = "count" if "count" in bs_created_data.columns else "quantity"

    for config in plot_configs:

        data = config["data"]
        name = config["name"]
        suffix = config["suffix"]
        # Creates a list of text to only show value on last point of the line
        texts = []
        if len(data) > 1:
            texts = [""] * (len(data) - 1) + [format_number(data[metric_name].iloc[-1])]

        if len(data) == 1:
            texts = [format_number(data[metric_name].iloc[-1])]

        hover_texts = [
            f"Semaine du {e[0]-timedelta(days=6):%d/%m} au {e[0]:%d/%m}<br><b>{format_number(e[1])}</b> {suffix}"
            for e in data.itertuples(index=False)
        ]

        scatter_list.append(
            go.Scatter(
                x=data["at"],
                y=data[metric_name],
                mode="lines+text",
                name=name,
                text=texts,
                textfont_size=15,
                textposition="middle right",
                hovertext=hover_texts,
                hoverinfo="text",
                line_shape="spline",
                line_smoothing=0.3,
                line_width=3,
            )
        )

    fig = go.Figure(scatter_list)

    fig.update_layout(
        paper_bgcolor="#fff",
        margin=dict(t=5, r=70, l=5),
        legend=dict(
            orientation="h", y=1.1, font_size=13, itemwidth=40, bgcolor="rgba(0,0,0,0)"
        ),
    )
    fig.update_xaxes(tick0="2022-01-03")
    fig.update_yaxes(side="right")

    return fig


def create_weekly_quantity_processed_figure(
    quantity_recovered: pd.Series, quantity_destroyed: pd.Series
) -> go.Figure:
    """Creates the figure showing the weekly waste quantity processed by type of process (destroyed or recovered).

    Parameters
    ----------
    quantity_recovered: Series
        Series containing the quantity of recovered waste aggregated by week.
    quantity_destroyed: Series
        Series containing the quantity of destroyed waste aggregated by week.

    Returns
    -------
    Plotly Figure Object
        Figure object ready to be plotted.
    """

    data_conf = [
        {
            "data": quantity_recovered,
            "name": "Déchets valorisés",
            "text": "Semaine du {0:%d/%m} au {1:%d/%m}<br><b>{2}</b> tonnes de déchets valorisées",
            "color": "#66673D",
        },
        {
            "data": quantity_destroyed,
            "name": "Déchets éliminés",
            "text": "Semaine du {0:%d/%m} au {1:%d/%m}<br><b>{2}</b> tonnes de déchets éliminées",
            "color": "#5E2A2B",
        },
    ]

    traces = []
    for conf in data_conf:

        data = conf["data"]
        traces.append(
            go.Bar(
                x=data.index,
                y=data,
                name=conf["name"],
                hovertext=[
                    conf["text"].format(
                        processed_at - timedelta(days=6),
                        processed_at,
                        format_number(quantity),
                    )
                    for processed_at, quantity in data.items()
                ],
                hoverinfo="text",
                text=data.apply(format_number),
                marker_color=conf["color"],
            )
        )

    fig = go.Figure(data=traces)

    max_value = sum([conf["data"].max() for conf in data_conf])
    fig.update_layout(
        xaxis_title="Semaine de traitement",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1,
            xanchor="left",
            x=0,
            title="Type de traitement :",
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(t=30, r=70, l=0),
        barmode="stack",
        yaxis_title="Quantité (en tonnes)",
        yaxis_range=[0, max_value * 1.1],
    )
    fig.update_yaxes(side="right")

    return fig


def create_quantity_processed_sunburst_figure(
    waste_quantity_processed_by_processing_code_df: pd.DataFrame,
) -> go.Figure:
    """Creates the figure showing the weekly waste quantity processed by type of processing operation (destroyed or recovered).

    Parameters
    ----------
    waste_quantity_processed_by_processing_code_df: DataFrame
        Aggregated DataFrame with quantity of processed waste by processing operation code, along with the description of the processing operation.

    Returns
    -------
    Plotly Figure Object
        Sunburst Figure object ready to be plotted.
    """

    agg_data = waste_quantity_processed_by_processing_code_df
    total_data = agg_data.groupby("type_operation").quantity.sum()
    agg_data_recycled = agg_data.loc[
        agg_data.type_operation == "Déchet valorisé"
    ].sort_values("quantity")
    agg_data_eliminated = agg_data.loc[
        agg_data.type_operation == "Déchet éliminé"
    ].sort_values("quantity")

    agg_data_recycled_other = agg_data_recycled.loc[
        (agg_data_recycled.quantity.cumsum() / agg_data_recycled.quantity.sum()) < 0.1
    ]
    agg_data_eliminated_other = agg_data_eliminated.loc[
        (agg_data_eliminated.quantity.cumsum() / agg_data_eliminated.quantity.sum())
        < 0.1
    ]

    agg_data_recycled_other_quantity = agg_data_recycled_other.quantity.sum()
    agg_data_eliminated_other_quantity = agg_data_eliminated_other.quantity.sum()

    agg_data_without_other = agg_data[
        ~agg_data.index.isin(
            agg_data_recycled_other.index.append(agg_data_eliminated_other.index)
        )
    ].sort_values("quantity", ascending=False)
    agg_data_without_other["colors"] = agg_data_without_other.type_operation.apply(
        lambda x: "rgb(102, 103, 61, 0.7)"
        if x == "Déchet valorisé"
        else "rgb(94, 42, 43, 0.7)"
    )

    ids = (
        total_data.index.to_list()
        + agg_data_without_other.processing_operation.to_list()
        + ["Autres opérations de valorisation", "Autres opérations d'élimination'"]
    )

    labels = (
        total_data.index.to_list()
        + agg_data_without_other.processing_operation.to_list()
        + ["Autres opérations"] * 2
    )
    parents = (
        ["", ""]
        + agg_data_without_other.type_operation.to_list()
        + ["Déchet valorisé", "Déchet éliminé"]
    )
    values = (
        total_data.to_list()
        + agg_data_without_other.quantity.to_list()
        + [agg_data_recycled_other_quantity, agg_data_eliminated_other_quantity]
    )
    colors = (
        ["rgb(102, 103, 61, 1)", "rgb(94, 42, 43, 1)"]
        + agg_data_without_other.colors.to_list()
        + ["rgb(102, 103, 61, 0.7)", "rgb(94, 42, 43, 0.7)"]
    )

    hover_text_template = "{code} : {description}<br><b>{quantity}t</b>"
    hover_texts = (
        [
            f"<b>{format_number(e)}t</b> {index.split(' ')[1]}es"
            for index, e in total_data.items()
        ]
        + [
            hover_text_template.format(
                code=e.processing_operation,
                description=e.processing_operation_description,
                quantity=format_number(e.quantity),
            )
            for e in agg_data_without_other.itertuples()
        ]
        + [
            f"Autres opérations de traitement<br><b>{format_number(e)}t</b> traités"
            for e in [
                agg_data_recycled_other_quantity,
                agg_data_eliminated_other_quantity,
            ]
        ]
    )

    fig = go.Figure(
        go.Sunburst(
            ids=ids,
            labels=labels,
            parents=parents,
            values=values,
            marker_colors=colors,
            branchvalues="total",
            texttemplate="%{label} - %{value:.3s}t soit <b>%{percentParent}</b>",
            hovertext=hover_texts,
            hoverinfo="text",
            sort=False,
            insidetextorientation="auto",
        )
    )
    fig.update_layout(margin=dict(t=0, l=0, r=0, b=0))

    return fig


def create_treemap_companies_figure(
    company_counts_by_section: pd.DataFrame, company_counts_by_division: pd.DataFrame
) -> go.Figure:
    """Creates the figure showing the number of companies by NAF category.

    Parameters
    ----------
    company_counts_by_section: DataFrame
        DataFrame containing the company counts by section.
    company_counts_by_division: DataFrame
        DataFrame containing the company counts by division

    Returns
    -------
    Plotly Figure Object
        Figure object ready to be plotted.
    """

    colors = [
        "rgba(64, 64, 122,0.4)",
        "rgba(112, 111, 211,0.4)",
        "rgba(247, 241, 227,0.4)",
        "rgba(52, 172, 224,0.4)",
        "rgba(51, 217, 178,0.4)",
        "rgba(44, 44, 84,0.4)",
        "rgba(71, 71, 135,0.4)",
        "rgba(170, 166, 157,0.4)",
        "rgba(34, 112, 147,0.4)",
        "rgba(33, 140, 116,0.4)",
        "rgba(255, 82, 82,0.4)",
        "rgba(255, 121, 63,0.4)",
        "rgba(209, 204, 192,0.4)",
        "rgba(255, 177, 66,0.4)",
        "rgba(255, 218, 121,0.4)",
        "rgba(179, 57, 57,0.4)",
        "rgba(132, 129, 122,0.4)",
        "rgba(204, 142, 53,0.4)",
        "rgba(204, 174, 98,0.4)",
        "rgba(205, 97, 51,0.4)",
        "rgba(77, 52, 42,0.4)",
    ]

    company_counts_by_section["colors"] = colors[
        : company_counts_by_section.code_section.nunique()
    ]

    company_counts_by_division["colors"] = company_counts_by_division[
        "libelle_section"
    ].apply(
        lambda x: company_counts_by_section.loc[
            company_counts_by_section.libelle_section == x, "colors"
        ].item()[:-4]
        + "1)",
    )

    company_counts_by_division = company_counts_by_division[
        company_counts_by_division["libelle_section"] != "Section NAF non renseignée."
    ]
    ids = (
        ["Tous les établissements"]
        + (
            "Tous les établissements/" + company_counts_by_section["libelle_section"]
        ).tolist()
        + (
            "Tous les établissements/"
            + company_counts_by_division["libelle_section"]
            + "/"
            + company_counts_by_division["libelle_division"]
        ).to_list()
    )

    labels = (
        [
            f"Tous les établissements - <b>{company_counts_by_section.num_entreprises.sum()/1000:.2f}k</b>"
        ]
        + (
            company_counts_by_section["libelle_section"].apply(
                break_long_line, max_line_length=36
            )
            + " - <b>"
            + company_counts_by_section["num_entreprises"].apply(
                lambda x: f"{x/1000:.1f}k" if x > 1000 else str(x)
            )
            + "</b>"
        ).tolist()
        + (
            company_counts_by_division["libelle_division"].apply(
                break_long_line, max_line_length=36
            )
            + " - <b>"
            + company_counts_by_division["num_entreprises"].apply(
                lambda x: f"{x/1000:.2f}k" if x > 1000 else str(x)
            )
            + "</b>"
        ).tolist()
    )

    parents = (
        [""]
        + ["Tous les établissements"] * len(company_counts_by_section)
        + (
            "Tous les établissements/" + company_counts_by_division["libelle_section"]
        ).tolist()
    )

    values = (
        [company_counts_by_section["num_entreprises"].sum()]
        + company_counts_by_section["num_entreprises"].tolist()
        + company_counts_by_division["num_entreprises"].to_list()
    )

    custom_data = (
        [""]
        + company_counts_by_section["code_section"].tolist()
        + company_counts_by_division["code_division"].to_list()
    )

    hover_texts = (
        [
            f"Tous les établissements - <b>{company_counts_by_section.num_entreprises.sum()/1000:.2f}k</b><extra></extra>"
        ]
        + (
            "<b>"
            + company_counts_by_section["num_entreprises"].apply(format_number)
            + "</b> établissements inscrits dans la section NAF "
            + company_counts_by_section["code_section"]
            + " - <i>"
            + company_counts_by_section["libelle_section"]
            + "</i><br>soit <b>"
            + (
                100
                * company_counts_by_section["num_entreprises"]
                / company_counts_by_section["num_entreprises"].sum()
            )
            .round(2)
            .astype(str)
            + "%</b> du total des établissements inscrits.<extra></extra>"
        ).tolist()
        + (
            "<b>"
            + company_counts_by_division["num_entreprises"].apply(format_number)
            + "</b> établissements inscrits dans la division NAF "
            + company_counts_by_division["code_division"]
            + " - <i>"
            + company_counts_by_division["libelle_division"]
            + "</i><br>soit <b>"
            + (
                100
                * company_counts_by_division["num_entreprises"]
                / company_counts_by_division["num_entreprises"].sum()
            )
            .round(2)
            .astype(str)
            + "%</b> du total des établissements inscrits.<extra></extra>"
        ).tolist()
    )

    colors = (
        ["#eeeeee"]
        + company_counts_by_section.colors.tolist()
        + company_counts_by_division.colors.tolist()
    )

    fig = go.Figure(
        go.Treemap(
            ids=ids,
            labels=labels,
            values=values,
            parents=parents,
            branchvalues="total",
            hovertemplate=hover_texts,
            customdata=custom_data,
            pathbar_thickness=25,
            marker_colors=colors,
            textposition="middle center",
            insidetextfont_size=100,
            tiling_packing="squarify",
            tiling_pad=5,
            outsidetextfont_size=100,
        )
    )
    fig.update_layout(margin={"l": 5, "r": 5, "t": 35, "b": 5}, height=800)
    return fig