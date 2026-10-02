-- Synthèse par commune du périmètre : combien de parcelles exposées, combien de cavités.
-- Une ligne par commune (code INSEE).

with parcelles as (
    select
        code_insee,
        count(*)                                                    as nb_parcelles,
        count(*) filter (where classe_exposition = 'forte')         as nb_parcelles_exposition_forte,
        count(*) filter (where classe_exposition = 'proximite')     as nb_parcelles_proximite,
        percentile_cont(0.5) within group (order by surface_m2)     as surface_mediane_m2
    from {{ ref('parcelles_exposition_cavites') }}
    group by code_insee
),

noms as (
    select code_insee, nom from {{ source('silver', 'perimetre_communes') }}
),

cavites as (
    select
        code_insee,
        count(*)                                                             as nb_cavites,
        count(*) filter (where type_cavite_code = 'ouvrage militaire')       as nb_ouvrages_militaires
    from {{ ref('stg_cavites') }}
    group by code_insee
)

select
    p.code_insee,
    noms.nom                                            as nom_commune,
    p.nb_parcelles,
    p.nb_parcelles_exposition_forte,
    p.nb_parcelles_proximite,
    -- % de parcelles exposées (forte + proximité), arrondi à 0,1
    round(100.0 * (p.nb_parcelles_exposition_forte + p.nb_parcelles_proximite) / p.nb_parcelles, 1)
                                                        as pct_parcelles_exposees,
    round(p.surface_mediane_m2::numeric, 0)             as surface_mediane_m2,
    -- cavités situées DANS la commune (une parcelle peut être exposée à une cavité voisine)
    coalesce(c.nb_cavites, 0)                           as nb_cavites,
    coalesce(c.nb_ouvrages_militaires, 0)               as nb_ouvrages_militaires
from parcelles p
left join noms using (code_insee)
left join cavites c using (code_insee)
