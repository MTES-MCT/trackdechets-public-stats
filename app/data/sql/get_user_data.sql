SELECT id,
    "createdAt"
FROM "default$default"."User"
WHERE "User"."isActive" = True
    and "createdAt"::date <= CURRENT_DATE - cast(
        extract(
            dow
            FROM CURRENT_DATE
        ) AS int
    )