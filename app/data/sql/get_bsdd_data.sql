select id,
    "created_at",
    "processed_at",
    "sent_at",
    "received_at",
    status,
    case
        when "quantity_received" > 60 then "quantity_received" / 1000
        else "quantity_received"
    END as "quantity",
    "processing_operation_done" as "processing_operation",
    "waste_details_code" as "waste_code",
    "waste_details_pop" as "waste_pop"
from "trusted_zone_trackdechets"."bsdd"
where "is_deleted" = false
    and "created_at" >= '2022-01-03'
    /* First day of the first week of the year */
    and "created_at" <= CURRENT_DATE - cast(
        extract(
            dow
            from CURRENT_DATE
        ) as int
    )
    and (
        (
            "processed_at" >= '1970-01-01'
            and "processed_at" < '2262-04-11'
            /* Due to pandas timestamp limitations */
        )
        or "processed_at" is null
    )
    and (
        (
            "sent_at" >= '1970-01-01'
            and "sent_at" < '2262-04-11'
        )
        or "sent_at" is null
    )
    and (
        (
            "received_at" >= '1970-01-01'
            and "received_at" < '2262-04-11'
        )
        or "received_at" is null
    )