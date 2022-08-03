select id,
    "default$default"."Form"."createdAt",
    "processedAt",
    "sentAt",
    "receivedAt",
    status,
    case
        when "quantityReceived" > 60 then "quantityReceived" / 1000
        else "quantityReceived"
    END as "weightValue",
    "recipientProcessingOperation" as "processingOperation",
    "wasteDetailsCode" as "wasteCode",
    "wasteDetailsPop" as "wastePop"
from "default$default"."Form"
where "Form"."isDeleted" = false
    and "createdAt" >= '2022-01-03'
    /* First day of the first week of the year */
    and "default$default"."Form"."createdAt"::date AT TIME ZONE 'Europe/Paris' <= CURRENT_DATE - cast(
        extract(
            dow
            from CURRENT_DATE
        ) as int
    )
    and (
        (
            "processedAt" >= '1970-01-01'
            and "processedAt" < '2262-04-11'
            /* Due to pandas timestamp limitations */
        )
        or "processedAt" is null
    )
    and (
        (
            "sentAt" >= '1970-01-01'
            and "sentAt" < '2262-04-11'
        )
        or "sentAt" is null
    )
    and (
        (
            "receivedAt" >= '1970-01-01'
            and "receivedAt" < '2262-04-11'
        )
        or "receivedAt" is null
    )