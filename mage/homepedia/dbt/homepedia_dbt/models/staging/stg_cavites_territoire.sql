-- Chaque cavité de France rattachée à sa commune ACTUELLE (code INSEE du COG 2026).
--
-- Le BRGM a recensé certaines cavités sous le code d'une commune fusionnée depuis, ou d'un
-- arrondissement (Lyon 3e = 69383). La table de correspondance (règles de Frank, voir
-- spark/jobs/clean_referentiel.py) ramène tous ces codes à la commune d'aujourd'hui.
-- commune_resolue = false : code absent du COG (à surveiller, voir le test dans _staging.yml).
{{ config(materialized='view') }}

select
    c.id_cavite,
    c.type_cavite_code,
    c.code_insee                         as code_insee_source,
    k.code_insee                         as code_insee,
    k.code_insee is not null             as commune_resolue
from {{ ref('stg_cavites') }} c
left join {{ source('silver', 'ref_correspondance_communes') }} k
    on k.code = c.code_insee
