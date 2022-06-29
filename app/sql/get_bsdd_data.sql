select id,
    "default$default"."Form"."createdAt",
    "processedAt",
    status,
    "quantityReceived",
    "recipientProcessingOperation"
from "default$default"."Form"
where "Form"."isDeleted" = false
    and "Form"."status" <> 'DRAFT'
    and (
        "default$default"."Form"."wasteDetailsCode" ~* '\*$'
        or "default$default"."Form"."wasteDetailsPop" = true
    )
    and cast("default$default"."Form"."createdAt" as date) >= '2022-01-01'
    and (
        cast("default$default"."Form"."processedAt" as date) >= '2022-01-01'
        or "processedAt" is null
    )
    and "default$default"."Form"."createdAt"::date <= CURRENT_DATE - cast(
        extract(
            dow
            FROM CURRENT_DATE
        ) AS int
    )
order by "createdAt" desc