select id,
    "created_at"
from "trusted_zone_trackdechets"."company"
where "created_at" <= CURRENT_DATE - cast(
        extract(
            dow
            from CURRENT_DATE
        ) as int
    )