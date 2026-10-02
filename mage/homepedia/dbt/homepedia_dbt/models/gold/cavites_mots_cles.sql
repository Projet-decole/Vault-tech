-- Ce que disent les descriptions en texte libre des cavités (recherche plein texte MongoDB).
-- Une ligne par (mot-clé, département). Part des fiches du département qui mentionnent le mot.

with mots as (
    select * from {{ source('silver', 'cavites_mots_cles') }}
),

fiches_par_departement as (
    -- nombre total de fiches cavités de chaque département (dénominateur du %)
    select departement, count(*) as nb_fiches_total
    from {{ source('silver', 'cavites') }}
    group by departement
)

select
    m.mot_cle,
    m.departement,
    m.nb_fiches,
    f.nb_fiches_total,
    round(100.0 * m.nb_fiches / f.nb_fiches_total, 1) as pct_fiches
from mots m
join fiches_par_departement f using (departement)
