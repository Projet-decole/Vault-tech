-- Indicateurs « cavités » par département (≈ 100 lignes), somme des communes, avec le contour du département.
{{ config(materialized='table') }}

{% set colonnes = ['nb_cavites', 'nb_ouvrages_militaires', 'nb_cavites_naturelles', 'nb_ouvrages_civils',
                   'nb_carrieres', 'nb_caves', 'nb_indeterminees', 'superficie_km2'] %}

with sommes as (
    select
        code_departement,
        count(*) as nb_communes,
        count(*) filter (where nb_cavites > 0) as nb_communes_avec_cavite,
        {% for c in colonnes -%}
        sum({{ c }}) as {{ c }}{{ ',' if not loop.last }}
        {% endfor %}
    from {{ ref('cavites_par_commune') }}
    group by code_departement
)
select
    d.code_departement,
    d.nom                                                         as nom_departement,
    d.code_region,
    r.nom                                                         as nom_region,
    s.nb_communes,
    s.nb_communes_avec_cavite,
    {% for c in colonnes -%}
    s.{{ c }},
    {% endfor -%}
    round((100 * s.nb_cavites / nullif(s.superficie_km2, 0))::numeric, 2)          as cavites_pour_100_km2,
    round((100.0 * s.nb_communes_avec_cavite / nullif(s.nb_communes, 0))::numeric, 1) as pct_communes_avec_cavite,
    d.geometrie_geojson
from {{ source('silver', 'ref_departements') }} d
join sommes s using (code_departement)
left join {{ source('silver', 'ref_regions') }} r on r.code_region = d.code_region
