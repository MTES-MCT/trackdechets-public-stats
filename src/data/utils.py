from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def get_data_date_interval_for_year(year: int = 2022) -> tuple[datetime, datetime]:
    now = datetime.now(tz=ZoneInfo("Europe/Paris"))

    date_interval = (
        datetime(year, 1, 1, tzinfo=ZoneInfo("Europe/Paris")),
        datetime(year + 1, 1, 1, tzinfo=ZoneInfo("Europe/Paris")),
    )
    date_start, date_end = date_interval

    if year == datetime.utcnow().year:
        max_date: datetime = now - timedelta(days=(now.toordinal() % 7) - 1)
        date_end = max_date.replace(hour=0, minute=0, second=0, microsecond=0)

    return date_start, date_end


def format_waste_codes(waste_code_list, add_top_level: bool = False):
    new_dict_list = []
    for waste_code_dict in waste_code_list:
        formatted_dict = {}
        formatted_dict["title"] = (
            waste_code_dict["code"]
            + " - "
            + waste_code_dict["description"].capitalize()
        )
        formatted_dict["value"] = waste_code_dict["code"]
        formatted_dict["key"] = waste_code_dict["code"]
        formatted_dict["children"] = format_waste_codes(waste_code_dict["children"])
        new_dict_list.append(formatted_dict)

    if add_top_level:
        new_dict_list = [
            {
                "title": "Tous les codes déchets",
                "value": "all",
                "key": "all",
                "children": new_dict_list,
            }
        ]
    return new_dict_list
