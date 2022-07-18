select id,
    "createdAt",
    "transporterTransportTakenOverAt" as "sentAt",
    "destinationReceptionDate" as "receivedAt",
    "destinationOperationSignatureDate" as "processedAt",
    "status",
    case
        when "weightValue" > 60 then "weightValue" / 1000
        else "weightValue"
    END as "weightValue",
    "destinationOperationCode" as "processingOperation",
    "wasteCode"
from "default$default"."Bsff"
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
            "destinationOperationSignatureDate" >= '1970-01-01'
            and "destinationOperationSignatureDate" < '2262-04-11'
        )
        or "destinationOperationSignatureDate" is null
    )