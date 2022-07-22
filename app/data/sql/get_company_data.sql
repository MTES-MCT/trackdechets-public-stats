select id,
    "createdAt"
from "default$default"."Company"
where "createdAt"::date <= CURRENT_DATE - cast(
        extract(
            dow
            from CURRENT_DATE
        ) as int
    )
    and "createdAt" >= '2022-01-03'