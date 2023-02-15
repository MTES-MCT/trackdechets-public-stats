SELECT
    id,
    "created_at" at time zone 'UTC' as created_at,
    "sent_at" at time zone 'UTC' as sent_at,
    "received_at" at time zone 'UTC' as received_at,
    "processed_at" at time zone 'UTC' as processed_at,
    status,
    CASE
        WHEN "quantity_received" > 60 THEN "quantity_received" / 1000
        ELSE "quantity_received"
    END AS "quantity",
    "processing_operation_done" AS "processing_operation",
    "waste_details_code" AS "waste_code",
    "waste_details_pop" AS "waste_pop",
    emitter_departement,
    emitter_region,
    recipient_departement as "destination_departement",
    recipient_region as "destination_region"
FROM
    "refined_zone_enriched"."bsdd_enriched"
WHERE
    "is_deleted" = FALSE
    AND "created_at" >= '2022-01-03'
    /* First day of the first week of the year */
    AND "created_at" <= CURRENT_DATE - CAST(
        EXTRACT(
            dow
            FROM
                CURRENT_DATE
        ) AS INT
    )
    AND (
        (
            "processed_at" >= '1970-01-01'
            AND "processed_at" < '2262-04-11'
            /* Due to pandas timestamp limitations */
        )
        OR "processed_at" IS NULL
    )
    AND (
        (
            "sent_at" >= '1970-01-01'
            AND "sent_at" < '2262-04-11'
        )
        OR "sent_at" IS NULL
    )
    AND (
        (
            "received_at" >= '1970-01-01'
            AND "received_at" < '2262-04-11'
        )
        OR "received_at" IS NULL
    )
    AND ((quantity_received < 100000)
    OR (quantity_received IS NULL))
