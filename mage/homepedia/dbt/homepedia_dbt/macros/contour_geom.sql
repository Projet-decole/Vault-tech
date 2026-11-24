-- Convertit un contour GeoJSON (texte) en vraie géométrie PostGIS, pour les tuiles vectorielles (Martin).
-- SRID 4326 = coordonnées GPS (longitude, latitude), celles des contours Etalab.
-- ST_MakeValid : 16 contours de communes se recoupent eux-mêmes ; on les répare,
-- puis ST_CollectionExtract(..., 3) ne garde que les polygones (la réparation peut laisser des lignes).
-- ST_Multi : tout en MultiPolygon, pour que la colonne ait un seul type déclaré (Martin la découvre seul).
{% macro contour_geom(colonne_geojson) -%}
    ST_Multi(ST_CollectionExtract(ST_MakeValid(
        ST_SetSRID(ST_GeomFromGeoJSON({{ colonne_geojson }}), 4326)), 3))::geometry(MultiPolygon, 4326)
{%- endmacro %}
