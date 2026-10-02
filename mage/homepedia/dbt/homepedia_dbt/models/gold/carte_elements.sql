-- Éléments à dessiner sur la carte Superset (graphique "deck.gl GeoJson") :
--   - les parcelles du périmètre (contour bleu)
--   - les cavités à moins de 500 m d'une parcelle (point rouge)
-- Une ligne = un objet GeoJSON "Feature" complet : forme + couleurs dans ses propriétés.
-- Coordonnées en GPS (EPSG:4326), comme l'attendent les cartes web.
-- Index sur nom_commune : le filtre obligatoire "Commune" du dashboard lit ~4 000 à 11 000 lignes
-- parmi ~1 million ; sans index, Postgres parcourrait toute la table (500 Mo) à chaque affichage.
{{ config(post_hook=["create index on {{ this }} (nom_commune)", "analyze {{ this }}"]) }}

with parcelles as (
    select
        'parcelle'                                   as type_element,
        id_parcelle                                  as identifiant,
        code_insee,
        nom_commune,
        'Parcelle ' || id_parcelle || ' (exposition ' || classe_exposition || ')' as libelle,
        -- Contour simplifié à 50 cm près (invisible à l'écran, fichier bien plus léger),
        -- reprojeté en GPS, 6 décimales (~10 cm)
        ST_AsGeoJSON(ST_Transform(ST_SimplifyPreserveTopology(geom, 0.5), 4326), 6)::json as geometrie,
        '#6baed6'                                    as couleur_remplissage,  -- bleu clair
        '#2171b5'                                    as couleur_contour       -- bleu foncé
    from {{ ref('parcelles_exposition_cavites') }}
),

cavites as (
    select
        'cavite'                                     as type_element,
        c.id_cavite                                  as identifiant,
        proche.code_insee,
        -- Commune de la parcelle la plus proche : le filtre "Commune" garde ainsi
        -- une cavité située juste de l'autre côté de la limite communale
        proche.nom_commune,
        initcap(c.type_cavite) || coalesce(' : ' || c.nom, '') as libelle,
        ST_AsGeoJSON(ST_Transform(c.geom, 4326), 6)::json      as geometrie,
        '#e31a1c'                                    as couleur_remplissage,  -- rouge
        '#67000d'                                    as couleur_contour       -- rouge foncé
    from {{ ref('stg_cavites') }} c
    -- Parcelle la plus proche, si elle est à moins de 500 m (index spatial du modèle gold)
    join lateral (
        select p.code_insee, p.nom_commune
        from {{ ref('parcelles_exposition_cavites') }} p
        where ST_DWithin(p.geom, c.geom, 500)
        order by p.geom <-> c.geom
        limit 1
    ) proche on true
    where c.localisation_fiable
),

elements as (
    select * from parcelles
    union all
    select * from cavites
)

select
    type_element,
    identifiant,
    code_insee,
    nom_commune,
    libelle,
    -- Feature GeoJSON : Superset lit fillColor / strokeColor dans les propriétés
    json_build_object(
        'type', 'Feature',
        'geometry', geometrie,
        'properties', json_build_object(
            'fillColor', couleur_remplissage,
            'strokeColor', couleur_contour,
            'libelle', libelle
        )
    )::text as geojson
from elements
