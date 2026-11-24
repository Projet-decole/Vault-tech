-- Indicateurs « cavités » pour CHAQUE commune de France (35 000 lignes), avec son contour.
-- Niveau commune de l'analyse multi-échelle exigée par le sujet (commune, département, région) ;
-- les niveaux département et région en sont des sommes (cavites_par_departement, cavites_par_region).
-- Une commune sans cavité est gardée (0) : sur une carte, « aucune cavité connue » est une information.
{{ config(
    materialized='table',
    post_hook=["create index on {{ this }} (code_departement)", "create index on {{ this }} (code_region)",
               "create index on {{ this }} using gist (geom)", "analyze {{ this }}"]
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
-- Parcelles exposées, depuis la synthèse du périmètre cadastral. Le cadastre découpe Paris, Lyon et
-- Marseille en arrondissements (69381 à 69389...) quand le référentiel ne connaît que la ville (69123) :
-- on rattache chaque arrondissement à sa ville.
parcelles as (
    select
        case when code_insee between '69381' and '69389' then '69123'
             when code_insee between '75101' and '75120' then '75056'
             when code_insee between '13201' and '13216' then '13055'
             else code_insee end                 as code_insee,
        sum(nb_parcelles)                        as nb_parcelles,
        sum(nb_parcelles_exposition_forte)       as nb_parcelles_exposition_forte,
        sum(nb_parcelles_proximite)              as nb_parcelles_proximite
    from {{ ref('communes_synthese') }}
    group by 1
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
    -- parcelles : seulement pour les communes du périmètre cadastral ; vide (null) ailleurs = « non analysée »,
    -- à ne pas confondre avec 0 parcelle exposée
    p.nb_parcelles                              as nb_parcelles_analysees,
    p.nb_parcelles_exposition_forte,
    p.nb_parcelles_proximite,
    round(100.0 * (p.nb_parcelles_exposition_forte + p.nb_parcelles_proximite) / nullif(p.nb_parcelles, 0), 1)
                                                as pct_parcelles_exposees,
    c.geometrie_geojson,
    -- le même contour en géométrie PostGIS (index spatial ci-dessus), pour la carte en tuiles (Martin)
    {{ contour_geom('c.geometrie_geojson') }}  as geom
from communes c
left join comptes k using (code_insee)
left join parcelles p using (code_insee)
left join {{ source('silver', 'ref_departements') }} d using (code_departement)
left join {{ source('silver', 'ref_regions') }} r on r.code_region = c.code_region
