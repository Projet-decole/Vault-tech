-- Question métier : chaque parcelle est-elle proche d'une cavité souterraine connue ?
-- Une ligne par parcelle. Toutes les distances sont en mètres (Lambert-93, EPSG:2154).
-- Index : géométrie (jointures spatiales), code_insee, et nom_commune (colonne filtrée par Superset).
{{ config(
    post_hook=[
        "create index on {{ this }} using gist (geom)",
        "create index on {{ this }} (code_insee)",
        "create index on {{ this }} (nom_commune)",
        "analyze {{ this }}"
    ]
) }}

-- "materialized" : la géométrie de chaque parcelle est calculée UNE fois et mise de côté.
-- Sans ça, la formule de la vue stg_parcelles (lecture du GeoJSON + reprojection) serait
-- recopiée et ré-exécutée pour chaque cavité comparée : 81 000 × 1 254 fois (16 min → quelques secondes).
with parcelles as materialized (
    select * from {{ ref('stg_parcelles') }}
)

-- NB : les cavités sont lues directement dans stg_cavites (pas via un WITH),
-- pour que Postgres puisse utiliser son index spatial GiST.

select
    p.id_parcelle,
    p.code_insee,
    communes.nom                                             as nom_commune,
    p.section,
    p.numero,
    p.contenance_m2,
    round(ST_Area(p.geom)::numeric, 0)                        as surface_m2,
    coalesce(voisines.nb_200m, 0)                            as nb_cavites_200m,
    coalesce(voisines.nb_500m, 0)                            as nb_cavites_500m,
    round(plus_proche.distance_m::numeric, 1)                as distance_cavite_la_plus_proche_m,
    plus_proche.id_cavite                                    as id_cavite_la_plus_proche,
    plus_proche.type_cavite                                  as type_cavite_la_plus_proche,
    case
        when coalesce(voisines.nb_200m, 0) > 0 then 'forte'
        when coalesce(voisines.nb_500m, 0) > 0 then 'proximite'
        else 'aucune'
    end                                                      as classe_exposition,
    -- Point garanti À L'INTÉRIEUR de la parcelle (un centroïde peut tomber dehors
    -- pour une parcelle en L), reconverti en GPS pour la carte Superset
    ST_X(ST_Transform(ST_PointOnSurface(p.geom), 4326))      as longitude,
    ST_Y(ST_Transform(ST_PointOnSurface(p.geom), 4326))      as latitude,
    p.geom

from parcelles p

-- Nom de la commune (la liste vient de config/perimetre.yml)
left join {{ source('silver', 'perimetre_communes') }} communes
    on communes.code_insee = p.code_insee

-- Pour CHAQUE parcelle (lateral = sous-requête exécutée ligne par ligne) :
-- compter les cavités à moins de 500 m, dont celles à moins de 200 m.
-- ST_DWithin utilise l'index spatial de stg_cavites : pas de comparaison avec les 1 263 cavités.
left join lateral (
    select
        count(*)                                           as nb_500m,
        count(*) filter (where ST_DWithin(c.geom, p.geom, 200)) as nb_200m
    from {{ ref('stg_cavites') }} c
    where c.localisation_fiable              -- seules les cavités bien localisées comptent
      and ST_DWithin(c.geom, p.geom, 500)
) voisines on true

-- Pour CHAQUE parcelle : la cavité la plus proche, quelle que soit la distance.
-- L'opérateur <-> ("distance à") parcourt l'index du plus proche au plus lointain.
left join lateral (
    select c.id_cavite, c.type_cavite, ST_Distance(c.geom, p.geom) as distance_m
    from {{ ref('stg_cavites') }} c
    where c.localisation_fiable
    order by c.geom <-> p.geom
    limit 1
) plus_proche on true
