-- Test "sur mesure" (singular test) : la requête doit renvoyer ZÉRO ligne pour réussir.
-- Vérifie que la classe d'exposition est cohérente avec la distance à la cavité la plus proche :
--   forte     ⇒ plus proche à ≤ 200 m
--   proximite ⇒ plus proche entre 200 et 500 m
--   aucune    ⇒ plus proche à > 500 m
-- Si une ligne ressort, les deux calculs (ST_DWithin et <->) ne sont pas d'accord : bug.
--
-- Attention à l'arrondi : la distance est stockée au décimètre. Une cavité à 500,02 m
-- (classe "aucune", à juste titre) apparaît à 500,0 m. Les bornes basses sont donc
-- testées en strict (< au lieu de ≤) : 500,0 arrondi reste compatible avec "au-delà de 500 m".

select id_parcelle, classe_exposition, distance_cavite_la_plus_proche_m
from {{ ref('parcelles_exposition_cavites') }}
where (classe_exposition = 'forte'     and distance_cavite_la_plus_proche_m > 200)
   or (classe_exposition = 'proximite' and (distance_cavite_la_plus_proche_m < 200 or distance_cavite_la_plus_proche_m > 500))
   or (classe_exposition = 'aucune'    and distance_cavite_la_plus_proche_m < 500)
