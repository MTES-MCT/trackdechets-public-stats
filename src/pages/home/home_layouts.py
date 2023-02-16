"""This module loads the layouts for several years of data.
Its allows to have a quick load as needed data is always in memory.

"""
from src.pages.home.home_layout_factory import get_layout_for_a_year

layout_2022 = get_layout_for_a_year(2022)
layout_2023 = get_layout_for_a_year(2023)

layouts = {2022: layout_2022, 2023: layout_2023}
