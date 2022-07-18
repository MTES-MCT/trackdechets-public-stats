select id,
    "createdAt",
    "transporterTakenOverAt" as "sentAt",
    "destinationReceptionDate" as "receivedAt",
    "destinationOperationDate" as "processedAt",
    "status",
    case
        when "emitterWasteWeightValue" > 60 then "emitterWasteWeightValue" / 1000
        else "emitterWasteWeightValue"
    END as "weightValue",
    "destinationOperationCode" as "processingOperation",
    "wasteCode"
from "default$default"."Bsdasri"
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
            "transporterTakenOverAt" >= '1970-01-01'
            and "transporterTakenOverAt" < '2262-04-11'
        )
        or "transporterTakenOverAt" is null
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