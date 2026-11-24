-- Cavités avec une vraie géométrie PostGIS (point), en Lambert-93 (mètres).
--
-- Exception à la règle "staging = vue" : on la matérialise en TABLE pour pouvoir
-- lui poser un index spatial (GiST), indispensable aux recherches "à moins de X mètres".
--
-- post_hook = SQL exécuté juste après la construction de la table :
--   1. l'index, SANS nom imposé : dbt reconstruit la table à côté de l'ancienne avant de supprimer
--      celle-ci ; un nom fixe serait encore pris par l'index de l'ancienne → index jamais recréé.
--   2. analyze : met à jour les statistiques, pour que Postgres sache que l'index vaut le coup.
{{ config(
    materialized='table',
    post_hook=[
        "create index on {{ this }} using gist (geom)",
        "analyze {{ this }}"
    ]
) }}

select
    id_cavite,
    nom,
    type_cavite,
    type_cavite_code,
    nature,
    statut,
    code_insee,
    positionnement,
    precision_xy_m,
    reperage,
    date_maj,
    -- Position utilisable pour un calcul de distance ?
    -- Non si pas de coordonnées, ou si le BRGM a seulement placé la cavité au centre de la commune.
    (srid is not null and positionnement is distinct from 'centroide de commune'
     and departement not like '97%') as localisation_fiable,
    -- x, y dans leur système d'origine (srid) → Lambert-93 (2154). NULL si pas de coordonnées.
    -- Métropole seulement : Lambert II étendu et Lambert-93 ne valent pas en outre-mer (départements 97x),
    -- où la conversion sort du globe et fait échouer toute la table (vécu le 24/11 avec les cavités de France).
    -- Les cavités d'outre-mer restent comptées par commune grâce à leur code INSEE (stg_cavites_territoire).
    case
        when srid is not null and departement not like '97%'
        then ST_Transform(ST_SetSRID(ST_MakePoint(x, y), srid), 2154)
    end as geom
from {{ source('silver', 'cavites') }}
