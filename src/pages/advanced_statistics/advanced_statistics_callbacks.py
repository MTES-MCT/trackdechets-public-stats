from dash import callback, Input, Output, State

from src.pages.advanced_statistics.advanced_statistics_layout_factory import (
    create_filtered_waste_processed_figure,
    create_input_output_elements,
)


@callback(
    inputs=[
        Input("departement-select", "value"),
        Input("waste-select", "checkedKeys"),
        State("waste-select", "halfCheckedKeys"),
    ],
    output=[Output("waste-processed-fig", "children")],
)
def create_figure_with_filter(
    departement_filter, waste_codes_filters_checked, waste_codes_filters_half_checked
):
    waste_codes_filters = {
        "checked": waste_codes_filters_checked,
        "half_checked": waste_codes_filters_half_checked,
    }
    return [
        create_filtered_waste_processed_figure(departement_filter, waste_codes_filters)
    ]


@callback(
    inputs=[
        Input("departement-select", "value"),
        Input("waste-select", "checkedKeys"),
        State("waste-select", "halfCheckedKeys"),
    ],
    output=[Output("total-processed-figures", "children")],
)
def create_figure_with_filter(
    departement_filter, waste_codes_filters_checked, waste_codes_filters_half_checked
):
    waste_codes_filters = {
        "checked": waste_codes_filters_checked,
        "half_checked": waste_codes_filters_half_checked,
    }
    return [create_input_output_elements(departement_filter, waste_codes_filters)]
