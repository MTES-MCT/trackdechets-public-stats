SELECT
    siret,
    nom_etablissement,
    code_commune_etablissement,
    array_to_string(codes_installations,',') as codes_installations,
    array_to_string(rubriques_autorisees,',') as rubriques_autorisees,
    latitude_etablissement,
    longitude_etablissement
FROM
    refined_zone_icpe.installations_enriched
WHERE
    rubriques_autorisees && ARRAY ['2790','2770','2760-1']
    and latitude_etablissement is not null
    and longitude_etablissement is not null
