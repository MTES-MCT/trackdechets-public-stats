import polars as pl


def format_filter(
    column_to_filter: pl.Expr, waste_codes_filter: dict[str, list[str]]
) -> pl.Expr | None:
    """
    Filter a given column column_to_filter based on the input waste_codes_filter.

    The filtering is done in three levels based on the length of the code: 2, 5, and longer than 5.
    The waste_codes_filter input is a dictionary that contains two keys: "checked" and "half_checked".
    The "checked" key holds a list of codes to be fully checked for filtering,
    while "half_checked" holds a list of codes to be partially checked for filtering.

    Parameters
    ----------
    column_to_filter : polars expression
        The column to be filtered.
    waste_codes_filter : dict
        The dictionary that contains the waste codes checked or half-checked on UI that will be used for filtering.

    Returns
    -------
    polars expression
        The filtered expression from column_to_filter. None if all filters or none filter have been checked.

   
    """
    series_filter = None

    checked = waste_codes_filter["checked"]
    if (checked != ["all"]) and (len(checked) > 0):

        first_level_filters = [e for e in checked if len(e) == 2]
        series_filter = column_to_filter.str.slice(0, 2).is_in(first_level_filters)

        half_checked = waste_codes_filter["half_checked"]
        half_checked = [e for e in half_checked if e != "all"]
        if len(half_checked) != 0:

            half_checked_first_level = [e for e in half_checked if len(e) == 2]
            second_level_filters = [
                e
                for e in checked
                if ((len(e) == 5) and (e[:2] in half_checked_first_level))
            ]
            if len(second_level_filters) > 0:
                series_filter = series_filter | column_to_filter.str.slice(0, 5).is_in(
                    second_level_filters
                )

            half_checked_second_level = [e for e in half_checked if len(e) == 5]
            third_level_filters = [
                e
                for e in checked
                if ((len(e) > 5) and (e[:5] in half_checked_second_level))
            ]
            if len(third_level_filters) > 0:
                series_filter = series_filter | column_to_filter.is_in(
                    third_level_filters
                )

    return series_filter
