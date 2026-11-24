-- Test "sur mesure" (singular test) : la requête doit renvoyer ZÉRO ligne pour réussir.
-- Vérifie qu'aucune parcelle ne se perd entre la synthèse du périmètre et les trois niveaux
-- (commune, département, région) : même total partout. Une parcelle perdue viendrait d'un code
-- commune absent du référentiel (ex. les arrondissements de Lyon, rattachés à 69123).

with totaux as (
    select 'commune' as niveau, sum(nb_parcelles_analysees) as total from {{ ref('cavites_par_commune') }}
    union all
    select 'departement', sum(nb_parcelles_analysees) from {{ ref('cavites_par_departement') }}
    union all
    select 'region', sum(nb_parcelles_analysees) from {{ ref('cavites_par_region') }}
)
select t.niveau, t.total, s.total as attendu
from totaux t
cross join (select sum(nb_parcelles) as total from {{ ref('communes_synthese') }}) s
where t.total is distinct from s.total
