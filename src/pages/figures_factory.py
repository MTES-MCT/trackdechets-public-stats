"""This modules contains all the functions to create the Plotly figure needed or the App.
"""
from datetime import datetime, timedelta
from typing import Dict, List

import plotly.graph_objects as go
import plotly.io as pio
import polars as pl

from src.pages.utils import break_long_line, format_number


def create_weekly_created_figure(
    data: pl.DataFrame,
) -> go.Figure:
    """Creates the figure showing number of weekly created companies, users...

    Parameters
    ----------
    data: DataFrame
        DataFrame containing the data to plot. Must have 'id' and 'at' columns.

    Returns
    -------
    Plotly Figure Object
        Figure object ready to be plotted.
    """

    data = data.to_dict(as_series=False)

    texts = []
    texts += [""] * (len(data) - 1) + [format_number(data["count"][-1])]

    hovertexts = [
        f"Semaine du {at-timedelta(days=6):%d/%m} au {at:%d/%m}<br><b>{format_number(count)}</b> créations"
        for at, count in zip(data["at"], data["count"])
    ]

    fig = go.Figure(
        [
            go.Scatter(
                x=data["at"],
                y=data["count"],
                text=texts,
                mode="lines+markers+text",
                hovertext=hovertexts,
                hoverinfo="text",
                textposition="middle right",
                textfont_size=15,
                line_shape="spline",
                line_smoothing=0.3,
                line_width=3,
            )
        ]
    )

    fig.update_layout(
        xaxis_title="Semaine de création",
        showlegend=False,
        paper_bgcolor="#fff",
        margin=dict(t=20, r=50, l=5),
    )
    fig.update_yaxes(side="right")

    return fig


def create_weekly_scatter_figure(
    bs_created_data: pl.DataFrame,
    bs_sent_data: pl.DataFrame,
    bs_received_data: pl.DataFrame,
    bs_processed_data: pl.DataFrame,
    bs_processed_non_final_data: pl.DataFrame,
    bs_processed_final_data: pl.DataFrame,
    bs_type: str,
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
    bs_processed_data: DataFrame
        DataFrame containing the count of 'bordereaux' processed.
        Must have 'at' and metric corresponding columns.
    bs_processed_non_final_data: DataFrame
        DataFrame containing the count of 'bordereaux' processed with non final processing operation code.
        Must have 'at' and metric corresponding columns.
    bs_processed_final_data: DataFrame
        DataFrame containing the count of 'bordereaux' processed with final processing operation code.
        Must have 'at' and metric corresponding columns.
    bs_type: str
        Type of 'bordereau'. Eg : BSDD, BSDA...
    lines_configs: list of dicts
        Configuration for the different traces. Must match the number of DataFrames (one config per DataFrame).

    Returns
    -------
    Plotly Figure Object
        Figure object ready to be plotted.
    """
    colors = list(pio.templates["gouv"]["layout"]["colorway"])  # type: ignore
    colors.append("#009099")
    plot_configs = [
        {"data": bs_created_data, **lines_configs[0], "color": colors[0]},
        {
            "data": bs_sent_data,
            **lines_configs[1],
            "color": colors[1],
            "visible": "legendonly",
        },
        {"data": bs_received_data, **lines_configs[2], "color": colors[2]},
        {
            "data": bs_processed_data,
            **lines_configs[3],
            "color": colors[3],
        },
        {
            "data": bs_processed_non_final_data,
            **lines_configs[4],
            "color": colors[4],
            "visible": "legendonly",
        },
        {
            "data": bs_processed_final_data,
            **lines_configs[5],
            "color": colors[5],
            "visible": "legendonly",
        },
    ]

    scatter_list = []

    metric_name = "count" if "count" in bs_created_data.columns else "quantity"
    y_title = "Quantité (en tonnes)" if metric_name == "quantity" else None
    legend_title = "Statut :" if metric_name == "quantity" else "Statut du bordereau :"

    for config in plot_configs:
        data = config["data"]

        if len(data) == 0:
            continue
        name = config["name"]
        suffix = config["suffix"]
        # Creates a list of text to only show value on last point of the line
        texts = []

        last_value = data[-1, 1]

        texts = [""] * (len(data) - 1) if len(data) > 1 else []
        custom_data = texts.copy()

        texts += [format_number(last_value)]

        custom_data += [format_number(last_value)]

        if metric_name == "count":
            suffix = f"{bs_type} {suffix}"

        hover_texts = [
            f"Semaine du {e[0]:%d/%m} au {e[0]+timedelta(days=6):%d/%m}<br><b>{format_number(e[1],1)}</b> {suffix}"
            for e in data.iter_rows()
        ]

        scatter_list.append(
            go.Scatter(
                x=data["at"],
                y=data[metric_name],
                mode="lines+text",
                name=name,
                text=texts,
                textfont_size=15,
                textfont_color=config["color"],
                textposition="middle right",
                hovertext=hover_texts,
                hoverinfo="text",
                line_shape="spline",
                line_smoothing=0.3,
                line_width=3,
                customdata=custom_data,
                visible=config.get("visible", True),
            )
        )

    fig = go.Figure(scatter_list)

    fig.update_layout(
        paper_bgcolor="#fff",
        margin=dict(t=25, r=70, l=15),
        legend=dict(
            orientation="v",
            y=1.2,
            x=-0.06,
            font_size=13,
            itemwidth=40,
            bgcolor="rgba(0,0,0,0)",
            title=legend_title,
        ),
        uirevision=True,
    )
    fig.update_xaxes(tick0="2022-01-03")
    fig.update_yaxes(side="right", title=y_title)

    return fig


def create_weekly_quantity_processed_figure(
    quantity_recovered: pl.Series,
    quantity_destroyed: pl.Series,
    date_axis_interval: tuple[datetime, datetime] | None = None,
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
        data = conf["data"].to_dict(as_series=False)
        traces.append(
            go.Bar(
                x=data["processed_at"],
                y=data["quantity"],
                name=conf["name"],
                hovertext=[
                    conf["text"].format(
                        processed_at - timedelta(days=6),
                        processed_at,
                        format_number(quantity),
                    )
                    for processed_at, quantity in zip(
                        data["processed_at"], data["quantity"]
                    )
                ],
                hoverinfo="text",
                texttemplate="%{y:.2s} tonnes",
                marker_color=conf["color"],
                width=1000 * 3600 * 24 * 6,
            )
        )

    fig = go.Figure(data=traces)

    max_value = sum([conf["data"]["quantity"].max() or 0 for conf in data_conf])

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

    if date_axis_interval is not None:
        fig.update_xaxes(range=date_axis_interval)

    return fig


def create_quantity_processed_sunburst_figure(
    waste_quantity_processed_by_processing_code_df: pl.DataFrame,
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
    total_data = (
        agg_data.groupby("type_operation")
        .agg(pl.col("quantity").sum())
        .sort("type_operation")
    )

    agg_data_recycled = agg_data.filter(
        pl.col("type_operation") == "Déchet valorisé"
    ).sort("quantity")
    agg_data_eliminated = agg_data.filter(
        pl.col("type_operation") == "Déchet éliminé"
    ).sort("quantity")

    agg_data_recycled_other = agg_data_recycled.filter(
        (pl.col("quantity") / pl.col("quantity").sum()) <= 0.12
    )
    agg_data_eliminated_other = agg_data_eliminated.filter(
        (pl.col("quantity") / pl.col("quantity").sum()) <= 0.21
    )

    agg_data_recycled_other_quantity = agg_data_recycled_other["quantity"].sum()
    agg_data_eliminated_other_quantity = agg_data_eliminated_other["quantity"].sum()

    other_processing_operations_codes = (
        pl.concat(
            [
                agg_data_recycled_other.select("processing_operation"),
                agg_data_eliminated_other.select("processing_operation"),
            ]
        )
        .unique()
        .to_series()
    )
    agg_data_without_other = agg_data.filter(
        pl.col("processing_operation").is_in(other_processing_operations_codes).is_not()
    ).sort("quantity", reverse=True)

    agg_data_without_other = agg_data_without_other.with_column(
        pl.col("type_operation")
        .apply(
            lambda x: "rgb(102, 103, 61, 0.7)"
            if x == "Déchet valorisé"
            else "rgb(94, 42, 43, 0.7)"
        )
        .alias("colors")
    )

    total_data = total_data.to_dict(as_series=False)
    agg_data_without_other = agg_data_without_other.to_dict(as_series=False)
    ids = (
        total_data["type_operation"]
        + agg_data_without_other["processing_operation"]
        + ["Autres opérations de valorisation", "Autres opérations d'élimination'"]
    )

    labels = (
        total_data["type_operation"]
        + agg_data_without_other["processing_operation"]
        + ["Autre"] * 2
    )
    parents = (
        ["", ""]
        + agg_data_without_other["type_operation"]
        + ["Déchet valorisé", "Déchet éliminé"]
    )
    values = (
        total_data["quantity"]
        + agg_data_without_other["quantity"]
        + [agg_data_recycled_other_quantity, agg_data_eliminated_other_quantity]
    )
    colors = (
        ["rgb(102, 103, 61, 1)", "rgb(94, 42, 43, 1)"]
        + agg_data_without_other["colors"]
        + ["rgb(102, 103, 61, 0.7)", "rgb(94, 42, 43, 0.7)"]
    )

    hover_text_template = "{code} : {description}<br><b>{quantity}t</b> traitées"
    hover_texts = (
        [
            f"<b>{format_number(e)}t</b> {index.split(' ')[1]}es"
            for index, e in zip(total_data["type_operation"], total_data["quantity"])
        ]
        + [
            hover_text_template.format(
                code=processing_operation,
                description=processing_operation_description,
                quantity=format_number(quantity),
            )
            for processing_operation, processing_operation_description, quantity in zip(
                agg_data_without_other["processing_operation"],
                agg_data_without_other["processing_operation_description"],
                agg_data_without_other["quantity"],
            )
        ]
        + [
            f"Autres opérations de traitement<br><b>{format_number(e)}t</b> traitées"
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
            texttemplate="%{label} - <b>%{percentRoot}</b>",
            hovertext=hover_texts,
            hoverinfo="text",
            sort=False,
            insidetextorientation="horizontal",
            insidetextfont_size=15,
        )
    )
    fig.update_layout(
        margin=dict(t=0, l=0, r=0, b=0),
    )

    return fig


def create_treemap_companies_figure(
    company_data: pl.DataFrame,
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

    df = company_data
    total_companies = df.height

    df = df.drop_nulls()
    categories = ["sous_classe", "classe", "groupe", "division", "section"]

    # build dfs at each granularity
    dfs = []
    for i, cat in enumerate(categories):
        agg_exprs = [
            pl.col("id").count().alias("count"),
            pl.col(f"libelle_{cat}").max(),
        ]

        id_sep = "#"

        id_exprs = [pl.lit("Tous les établissements")]
        if i < (len(categories) - 1):
            for tmp_cat in reversed(categories[i + 1 :]):
                id_exprs.append(pl.col(f"libelle_{tmp_cat}").max())
        id_exprs.append(pl.col(f"libelle_{cat}").max())
        agg_exprs.append(pl.concat_str(id_exprs, sep=id_sep).alias("ids"))

        temp_df = df.groupby(f"code_{cat}", maintain_order=True).agg(agg_exprs)

        parent_exp = (
            pl.col("ids")
            .str.split(id_sep)
            .arr.reverse()
            .arr.slice(1)
            .arr.reverse()
            .arr.join(id_sep)
            .alias("parents")
        )

        labels_expr = pl.concat_str(
            [
                pl.col(f"libelle_{cat}").apply(lambda x: break_long_line(x, 14)),
                pl.lit(" - <b>"),
                pl.col("count").apply(
                    lambda x: f"{x/1000:.1f}k" if x > 1000 else str(x)
                ),
                pl.lit("</b>"),
            ]
        ).alias("labels")

        hover_exp = pl.concat_str(
            [
                pl.lit("<b>"),
                pl.col("count").apply(format_number),
                pl.lit("</b> établissements inscrits dans la section NAF "),
                pl.col(f"code_{cat}"),
                pl.lit(" - <i>"),
                pl.col(f"libelle_{cat}"),
                pl.lit("</i><br>soit <b>"),
                (100 * pl.col("count") / total_companies).round(2).cast(pl.Utf8),
                pl.lit("%</b> du total des établissements inscrits.<extra></extra>"),
            ]
        ).alias("hover_texts")

        dfs.append(temp_df.with_columns([labels_expr, hover_exp, parent_exp]))

    # Build plotly necessaries lists
    ids = ["Tous les établissements"]
    labels = [f"Tous les établissements - <b>{total_companies/1000:.2f}k</b>"]
    parents = [""]
    values = [total_companies]
    hover_texts = [
        f"Tous les établissements - <b>{total_companies/1000:.2f}k</b><extra></extra>"
    ]
    for df in reversed(dfs):
        json = df.to_dict(as_series=False)
        ids.extend(json["ids"])
        labels.extend(json["labels"])
        parents.extend(json["parents"])
        values.extend(json["count"])
        hover_texts.extend(json["hover_texts"])

    fig = go.Figure(
        go.Treemap(
            ids=ids,
            labels=labels,
            values=values,
            parents=parents,
            branchvalues="total",
            hovertemplate=hover_texts,
            pathbar_thickness=35,
            textposition="middle center",
            tiling_packing="squarify",
            insidetextfont_size=300,
            tiling_pad=3,
            maxdepth=2,
        )
    )
    fig.update_layout(
        margin={"l": 5, "r": 5, "t": 35, "b": 5},
        height=800,
        template="seaborn",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig
