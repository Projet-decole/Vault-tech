-- Exécuté automatiquement au premier démarrage du conteneur postgres
-- (uniquement si le volume de données est vide).

-- Active PostGIS : type geometry, SRID, fonctions ST_Distance, ST_DWithin...
CREATE EXTENSION IF NOT EXISTS postgis;

-- silver : données nettoyées et typées, écrites par Spark
CREATE SCHEMA IF NOT EXISTS silver;

-- gold : tables métier prêtes à l'emploi, construites par dbt, lues par Superset
CREATE SCHEMA IF NOT EXISTS gold;
