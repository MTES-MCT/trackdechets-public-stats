SELECT id,
    "createdAt"
FROM "default$default"."User"
WHERE "User"."isActive" = True
    and cast("createdAt" as date) >= '2022-01-01'
    and "createdAt"::date <= CURRENT_DATE - cast(
        extract(
            dow
            FROM CURRENT_DATE
        ) AS int
    )
ORDER BY createdAt