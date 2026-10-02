-- Fiches des fichiers médias (images, PDF...) rangés dans le bucket S3 "medias" (SeaweedFS).
-- La base ne contient PAS le fichier, seulement de quoi le retrouver et le relier aux autres données.
-- Écrite par le bloc Mage fetch_orthophotos ; créée ici pour exister dès le premier dbt build.
-- (Exécuté au premier démarrage de Postgres seulement ; le bloc la crée aussi si elle manque.)

CREATE TABLE IF NOT EXISTS silver.medias (
    cle            text PRIMARY KEY,      -- chemin dans le bucket, ex. orthophotos/57704/LORAW0005855.jpg
    bucket         text NOT NULL,         -- "medias"
    type_objet     text NOT NULL,         -- à quoi se rattache le média : "cavite", "parcelle"...
    id_objet       text NOT NULL,         -- identifiant de cet objet (id_cavite...)
    type_media     text NOT NULL,         -- "orthophoto", "pdf"...
    url_publique   text NOT NULL,         -- adresse lisible par le navigateur (Superset)
    source_url     text,                  -- d'où vient le fichier
    licence        text,
    octets         integer,
    telecharge_le  timestamptz NOT NULL DEFAULT now()
);

-- Un seul média d'un type donné par objet (ex. une seule orthophoto par cavité) :
-- si un bug tente d'en ajouter une deuxième, Postgres refuse au lieu de créer un doublon silencieux.
CREATE UNIQUE INDEX IF NOT EXISTS medias_un_par_objet ON silver.medias (type_objet, id_objet, type_media);
