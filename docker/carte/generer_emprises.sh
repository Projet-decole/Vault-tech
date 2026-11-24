#!/bin/sh
# Écrit docker/carte/page/emprises.json : le rectangle englobant (ouest, sud, est, nord) de chaque région
# et de chaque département, par nom. La carte s'en sert pour se recentrer sur la sélection des filtres.
# À relancer si les contours changent (depuis la racine du projet, PostgreSQL lancé) :
#     sh docker/carte/generer_emprises.sh
set -e
# La requête passe par l'entrée standard de psql (évite les problèmes de guillemets du shell)
docker exec -i homepedia-postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -At' > docker/carte/page/emprises.json <<'SQL'
with emprises as (
    select 'regions' as niveau, nom_region as nom, geom from gold.cavites_par_region
    union all
    select 'departements', nom_departement, geom from gold.cavites_par_departement
)
select json_object_agg(niveau, contenu)
from (
    select niveau, json_object_agg(nom, json_build_array(
        round(ST_XMin(geom)::numeric, 3), round(ST_YMin(geom)::numeric, 3),
        round(ST_XMax(geom)::numeric, 3), round(ST_YMax(geom)::numeric, 3))) as contenu
    from emprises
    group by niveau
) t;
SQL
echo "docker/carte/page/emprises.json écrit ($(wc -c < docker/carte/page/emprises.json) octets)"
