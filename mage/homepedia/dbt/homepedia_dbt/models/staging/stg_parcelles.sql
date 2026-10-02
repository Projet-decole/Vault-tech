-- Parcelles avec une vraie géométrie PostGIS, en Lambert-93 (mètres).
-- Vue : rien n'est stocké, la conversion est refaite à chaque lecture.

select
    id_parcelle,
    code_insee,
    prefixe,
    section,
    numero,
    contenance_m2,
    arpente,
    date_creation,
    date_maj,
    ingest_date,
    -- texte GeoJSON → géométrie GPS (SRID 4326) → Lambert-93 (SRID 2154, en mètres)
    ST_Transform(
        ST_SetSRID(ST_GeomFromGeoJSON(geometrie_geojson), 4326),
        2154
    ) as geom
from {{ source('silver', 'parcelles') }}
