-- Indicateurs « cavités » pour CHAQUE commune de France (35 000 lignes), avec son contour.
-- Niveau commune de l'analyse multi-échelle exigée par le sujet (commune, département, région) ;
-- les niveaux département et région en sont des sommes (cavites_par_departement, cavites_par_region).
-- Une commune sans cavité est gardée (0) : sur une carte, « aucune cavité connue » est une information.
{{ config(
    materialized='table',
    post_hook=["create index on {{ this }} (code_departement)", "create index on {{ this }} (code_region)",
               "analyze {{ this }}"]
) }}

{% set familles = {
    'nb_ouvrages_militaires': 'ouvrage militaire',
    'nb_cavites_naturelles': 'naturelle',
    'nb_ouvrages_civils': 'ouvrage civil',
    'nb_carrieres': 'carriere',
    'nb_caves': 'cave',
    'nb_indeterminees': 'indetermine'
} %}

with comptes as (
    select
        code_insee,
        count(*) as nb_cavites,
        {% for colonne, code in familles.items() -%}
        count(*) filter (where type_cavite_code = '{{ code }}') as {{ colonne }}{{ ',' if not loop.last }}
        {% endfor %}
    from {{ ref('stg_cavites_territoire') }}
    where commune_resolue
    group by code_insee
),
communes as (
    select
        c.*,
        -- surface réelle sur l'ellipsoïde (geography) : juste aussi en outre-mer, où Lambert-93 ne vaut rien
        ST_Area(ST_GeomFromGeoJSON(c.geometrie_geojson)::geography) / 1e6 as superficie_km2
    from {{ source('silver', 'ref_communes') }} c
)
select
    c.code_insee,
    c.nom                                       as nom_commune,
    c.code_departement,
    d.nom                                       as nom_departement,
    c.code_region,
    r.nom                                       as nom_region,
    coalesce(k.nb_cavites, 0)                   as nb_cavites,
    {% for colonne in familles -%}
    coalesce(k.{{ colonne }}, 0)                as {{ colonne }},
    {% endfor -%}
    round(c.superficie_km2::numeric, 2)         as superficie_km2,
    -- densité pour 100 km² : compare des communes de tailles très différentes
    round((100 * coalesce(k.nb_cavites, 0) / nullif(c.superficie_km2, 0))::numeric, 2)
                                                as cavites_pour_100_km2,
    c.geometrie_geojson
from communes c
left join comptes k using (code_insee)
left join {{ source('silver', 'ref_departements') }} d using (code_departement)
left join {{ source('silver', 'ref_regions') }} r on r.code_region = c.code_region
