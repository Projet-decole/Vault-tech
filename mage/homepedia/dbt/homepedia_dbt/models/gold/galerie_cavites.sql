-- Galerie : tout ce qu'on sait d'une cavité affichée sur la carte, en une ligne :
-- identité, commune, description en TEXTE LIBRE et PHOTO AÉRIENNE (fichier du bucket S3).
-- Vue (et non table) : une photo téléchargée après le dbt build apparaît immédiatement.
{{ config(materialized='view') }}

select
    c.identifiant                                  as id_cavite,
    s.nom,
    s.type_cavite,
    c.code_insee,
    c.nom_commune,
    s.precision_xy_m,
    sc.commentaires,
    m.url_publique                                 as url_photo,
    -- Balise HTML affichée telle quelle par le tableau Superset (option "rendu HTML")
    '<img src="' || m.url_publique || '" width="220" alt="Photo aérienne © IGN">' as photo
from {{ ref('carte_elements') }} c
join {{ ref('stg_cavites') }} s
    on s.id_cavite = c.identifiant
join {{ source('silver', 'cavites') }} sc
    on sc.id_cavite = c.identifiant
join {{ source('silver', 'medias') }} m
    on m.id_objet = c.identifiant and m.type_objet = 'cavite' and m.type_media = 'orthophoto'
where c.type_element = 'cavite'
