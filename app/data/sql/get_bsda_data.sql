select id,
    "createdAt",
    "transporterTransportTakenOverAt" as "sentAt",
    "destinationReceptionDate" as "receivedAt",
    "destinationOperationDate" as "processedAt",
    "status",
    case
        when "weightValue" > 60 then "weightValue" / 1000
        else "weightValue"
    END as "weightValue",
    "destinationOperationCode" as "processingOperation",
    "wasteCode",
    "wastePop"
from "default$default"."Bsda"
where "isDeleted" = false
    and "createdAt" >= '2022-01-03'
    /* First day of the first week of the year */
    and "createdAt"::date <= CURRENT_DATE - cast(
        extract(
            dow
            from CURRENT_DATE
        ) as int
    )
    /* Due to pandas timestamp limitations */
    and (
        (
            "transporterTransportTakenOverAt" >= '1970-01-01'
            and "transporterTransportTakenOverAt" < '2262-04-11'
        )
        or "transporterTransportTakenOverAt" is null
    )
    and (
        (
            "destinationReceptionDate" >= '1970-01-01'
            and "destinationReceptionDate" < '2262-04-11'
        )
        or "destinationReceptionDate" is null
    )
    and (
        (
            "destinationOperationDate" >= '1970-01-01'
            and "destinationOperationDate" < '2262-04-11'
        )
        or "destinationOperationDate" is null
    )