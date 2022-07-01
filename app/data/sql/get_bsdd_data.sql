select id,
    "default$default"."Form"."createdAt",
    "processedAt",
    status,
    case
        when "quantityReceived" > 60 then "quantityReceived" / 1000
        else "quantityReceived"
    END as "quantityReceived",
    "recipientProcessingOperation"
from "default$default"."Form"
where "Form"."isDeleted" = false
    and "Form"."status" <> 'DRAFT'
    and (
        "default$default"."Form"."wasteDetailsCode" ~* '\*$'
        or "default$default"."Form"."wasteDetailsPop" = true
    )
    and "createdAt" >= '2022-01-01'
    and (
        (
            "processedAt" >= "createdAt"
            and "processedAt"::date AT TIME ZONE 'Europe/Paris' <= CURRENT_DATE - cast(
                extract(
                    dow
                    from CURRENT_DATE
                ) as int
            )
        )
        or "processedAt" is null
    )
    and "default$default"."Form"."createdAt"::date AT TIME ZONE 'Europe/Paris' <= CURRENT_DATE - cast(
        extract(
            dow
            from CURRENT_DATE
        ) as int
    )
order by "processedAt" desc nulls last