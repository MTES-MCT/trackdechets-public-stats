from dash import Input, Output, State, callback
from dash.development.base_component import Component

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
    output=Output("waste-processed-fig", "children"),
)
def create_waste_processed_figure(
    departement_filter: str,
    waste_codes_filters_checked: list[str],
    waste_codes_filters_half_checked: list[str],
) -> list[Component]:
    """
    Creates a filtered figure for waste processed by merging checked and half-checked waste codes.

    Parameters:
    ----------
    departement_filter : str
        The selected departement code (INSEE code) for the filter.
    waste_codes_filters_checked : list
        List of waste codes checked by the user.
    waste_codes_filters_half_checked : list
        List of waste codes that are half-checked by the user.

    Returns:
    -------
    list
        A list containing the filtered waste processed figure.

    """
    waste_codes_filters = {
        "checked": waste_codes_filters_checked,
        "half_checked": waste_codes_filters_half_checked,
    }
    return create_filtered_waste_processed_figure(
        departement_filter, waste_codes_filters
    )


@callback(
    inputs=[
        Input("departement-select", "value"),
        Input("waste-select", "checkedKeys"),
        State("waste-select", "halfCheckedKeys"),
    ],
    output=Output("total-processed-figures-container", "children"),
)
def create_waste_processed_numbers(
    departement_filter: str,
    waste_codes_filters_checked: list[str],
    waste_codes_filters_half_checked: list[str],
) -> list[Component]:
    """
    Creates dash elements containing the three figures computed after data is filtered by given filter values:
    - Total number of processed waste incoming
    - Total number of waste outgoing
    - Total number of waste created and processed inside the departement.

    If no department value is selected, figures are not computed and instead an informational message is returned.

    Parameters
    ----------
    departement_filter: str
        Filter based on departement.
    waste_codes_filters_checked: list[str]
        Filter based on checked waste codes.
    waste_codes_filters_half_checked: list[str]
        Filter based on half-checked waste codes.

    Returns
    -------
    list
        List of elements to display the total number of processed waste.

    """
    waste_codes_filters = {
        "checked": waste_codes_filters_checked,
        "half_checked": waste_codes_filters_half_checked,
    }
    return create_input_output_elements(departement_filter, waste_codes_filters)
