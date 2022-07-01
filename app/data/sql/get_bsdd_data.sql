select id,
    "default$default"."Form"."createdAt",
    "processedAt",
    "sentAt",
    "receivedAt",
    status,
    case
        when "quantityReceived" > 60 then "quantityReceived" / 1000
        else "quantityReceived"
    END as "quantityReceived",
    "recipientProcessingOperation",
    "wasteDetailsCode",
    "wasteDetailsPop"
from "default$default"."Form"
where "Form"."isDeleted" = false
    and "createdAt" >= '2022-01-01'
    and "default$default"."Form"."createdAt"::date AT TIME ZONE 'Europe/Paris' <= CURRENT_DATE - cast(
        extract(
            dow
            from CURRENT_DATE
        ) as int
    )
    and (
        "processedAt" >= '1970-01-01'
        or "processedAt" is null
    )
    and (
        "sentAt" >= '1970-01-01'
        or "sentAt" is null
    )