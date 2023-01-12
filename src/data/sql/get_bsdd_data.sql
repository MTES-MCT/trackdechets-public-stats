SELECT
    id,
    "created_at",
    "processed_at",
    "sent_at",
    "received_at",
    status,
    CASE
        WHEN "quantity_received" > 60 THEN "quantity_received" / 1000
        ELSE "quantity_received"
    END AS "quantity",
    "processing_operation_done" AS "processing_operation",
    "waste_details_code" AS "waste_code",
    "waste_details_pop" AS "waste_pop"
FROM
    "trusted_zone_trackdechets"."bsdd"
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
    AND ((quantity_received < 700000)
    OR (quantity_received IS NULL))