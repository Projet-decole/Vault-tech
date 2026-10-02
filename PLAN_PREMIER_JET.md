# Plan — Premier jet du pipeline HOMEPEDIA

> Plan d'exécution destiné à un agent de code, à dérouler **avec** l'utilisateur.
> Rédigé le 2026-09-25. Les explications pédagogiques de chaque étape sont dans l'artefact « Chantier HOMEPEDIA ».

## ✅ État au 2026-09-26 : phases 0 à 7 et phase bonus réalisées

Le premier jet est **terminé** : `homepedia_full` (Mage) tourne de bout en bout en ~95 s, dbt passe 37 tests,
le dashboard Superset est versionné, et l'ajout d'une commune (même d'un autre département) se fait
dans `config/perimetre.yml` seulement. Mode d'emploi : **`README.md`**. Le plan ci-dessous est conservé
tel qu'écrit à l'origine ; voici les **écarts** décidés en cours de route :

| Sujet | Plan initial | Réalisé | Pourquoi |
|---|---|---|---|
| Source cavités | API Géorisques `cavites` | Export CSV départemental `webappReport` | API et WFS BRGM hors service (503) ; voir fiche source |
| Coordonnées cavités en silver | longitude / latitude | `x`, `y`, `srid` ; conversion dans dbt (PostGIS) | Colonnes brutes dans plusieurs projections selon les lignes |
| Département | un seul (`57`) | déduit du code INSEE, multi-départements | Test avec le Rhône (69) |
| Versions | à vérifier | PostGIS 17-3.5, Mage 0.9.79, Hadoop 3.4.3, Spark 4.1.3, Superset 6.1.0, dbt 1.8.7 | Spark 4.1.3 = même Python (3.10) que Mage |
| pyspark dans Mage | installé dans l'image | dans un virtualenv séparé `/opt/pyspark` | Si Mage voit pyspark, il ouvre une session Spark à chaque bloc (×20 sur le temps) |
| `stg_cavites` | vue | table (+ index GiST) | Un index spatial ne se pose pas sur une vue |
| Carte Superset | deck.gl Scatter (centroïdes) | deck.gl GeoJson : contours des parcelles + cavités (`gold.carte_elements`) | Plus lisible (demande utilisateur) |
| Dashboard | construit à la main | versionné dans `docker/superset/dashboard/`, importé au 1er démarrage | Reproductible pour tout le groupe |
| Orchestration | `homepedia_full` = 3 pipelines enchaînés | un seul DAG de 10 blocs réutilisant ceux des pipelines d'étape | Dépendances explicites (dbt attend Spark ET la liste des communes) |
| Bonus — stockage de fichiers | MinIO | SeaweedFS 4.47 (mode `mini`), bucket `medias` | MinIO n'est plus publié sur Docker Hub |
| Bonus — médias | PDF de plans de prévention (API Géorisques) | Photo aérienne IGN (WMS) de chaque cavité de la carte, galerie Superset | API Géorisques en panne ; une photo parle davantage |
| Bonus — MongoDB | réponses JSON de l'API, agrégation `$group` | Fiches cavités complètes (Spark + connecteur 11.1.0), index plein texte français + 2dsphere, mots-clés → Postgres gold | Superset ne lit pas MongoDB : résultats préparés dans Postgres |
| dbt dans Mage | `dbt build` | `dbt build --no-partial-parse` | Le cache d'analyse ignorait des tests sans erreur |
| Échelle — périmètre | 5 à 10 communes | Rhône entier (option `departements:`) + 6 communes de Moselle : 280 communes, ~1 M parcelles | Passage à l'échelle |
| Échelle — ingestion | blocs qui se passent les données en mémoire | un bloc `ingest_cadastre` en flux (une commune en mémoire à la fois) | Mémoire de Mage stable (~0,9 Go) quel que soit le volume |
| Échelle — Spark | relit tout l'historique bronze | lit la dernière `ingest_date` de chaque département ; 4 cœurs / 3 Go | Le bronze grossit à chaque exécution |
| Échelle — Superset | carte de toutes les parcelles | filtre Commune obligatoire (défaut Veckring), top 25 en barres, index `nom_commune` | 1 M de contours = ~350 Mo : illisible et trop lourd pour un navigateur |

Reste à faire : catalogue des cas d'usage (brief : `docs/brief-catalogue-cas-usage.md`), passage à l'échelle n°2 : cluster multi-PC → plan prêt : `docs/PLAN_CLUSTER.md`.

---

## 0. Contexte à lire avant de commencer

- **Projet** : plateforme big data (projet d'école) pour les entreprises de construction et de rénovation de bunkers. On croise des sources ouvertes pour qualifier des terrains.
- **Architecture cible** (`data_pipeline_flow.png`) :
  `Sources ouvertes → Mage.ai → Hadoop HDFS → Spark → PostgreSQL (silver) → dbt (gold) → Apache Superset`,
  avec en parallèle `Spark → MongoDB` (textes, avis, JSON) et `Mage.ai → Bucket médias` (images, PDF).
- **L'utilisateur débute sur tous ces outils.** Le but du premier jet est qu'il **comprenne** chaque brique, pas seulement que ça tourne.

### Règles de conduite pour l'agent

1. **Une phase à la fois.** À la fin de chaque phase : lancer la vérification, montrer le résultat à l'utilisateur, lui expliquer en 3-5 phrases ce qui vient de se passer, et attendre son feu vert avant la phase suivante.
2. **Le plus simple qui marche.** Pas d'optimisation, pas de sécurité de prod (mots de passe dans `.env`, c'est suffisant), pas de haute disponibilité.
3. **Rien de magique.** Chaque fichier de config créé doit contenir des commentaires courts qui disent à quoi sert chaque ligne non évidente.
4. **Vérifier plutôt que supposer.** Les tags d'images Docker, les paramètres d'API et les noms de champs indiqués ici sont des points de départ : les confirmer (doc officielle, `curl`, `docker pull`) avant de les figer.
5. **Si un point bloque plus de ~15 min** (ex. incompatibilité de versions Spark/Hadoop), s'arrêter et revenir vers l'utilisateur avec le constat et 2 options.

---

## 1. Objectif et périmètre

**Question métier du premier jet :**
> *Sur un petit territoire mosellan, quelles parcelles cadastrales sont situées à proximité d'une cavité souterraine connue (carrière, mine, sape de guerre, ouvrage) ?*

Pour un constructeur de bunkers, une cavité proche est soit un **risque** (effondrement), soit une **opportunité** (cavité réutilisable). C'est un premier indicateur utile, et la jointure spatiale oblige à traverser toute la chaîne.

**Sources (2) :**

| Source | Producteur | Accès | Format | Rôle |
|---|---|---|---|---|
| Cadastre Etalab — parcelles | DGFiP / Etalab | `https://cadastre.data.gouv.fr/data/etalab-cadastre/latest/geojson/communes/{dep}/{insee}/cadastre-{insee}-parcelles.json.gz` (URL de département aussi dispo : `.../departements/57/cadastre-57-parcelles.json.gz`) | GeoJSON gzippé, WGS84 (EPSG:4326) | Référentiel des terrains |
| Cavités souterraines (BD Cavités) | BRGM / Géorisques | API Géorisques v1, endpoint `cavites` (doc Swagger : https://www.georisques.gouv.fr/doc-api). Repli si l'API est indisponible : export BD Cavités sur data.gouv.fr (« inventaire des cavités souterraines ») | JSON paginé (API) ou CSV (export) | Points de cavités |

> ⚠️ Le 2026-09-25, l'API Géorisques renvoyait une `503`. En phase 1, vérifier son état ; si elle reste indisponible, basculer sur l'export CSV.
>
> ✅ **Décision phase 1 (2026-09-25)** : API v1/v2 et WFS BRGM KO → on utilise l'export CSV départemental
> `https://www.georisques.gouv.fr/webappReport/ws/cavites/departements/57/fiches.csv?`, filtré ensuite sur `numInsee`.
> Coordonnées : `xouvl2e/youvl2e` en **EPSG:27572** (Lambert II étendu), reprojetées dans PostGIS. Spark garde donc x/y + SRID dans `silver.cavites`, et la conversion en longitude/latitude se fait dans dbt (`stg_cavites`).
> Détails : `docs/fiches-sources/cavites-bdcavites.md`.

**Territoire :** 5 à 10 communes de Moselle (dép. 57), le long de l'ancienne ligne Maginot et du bassin ferrifère (riche en cavités). Proposition : Thionville, Hayange, Veckring, Hettange-Grande, Algrange, Metz. **Ne pas coder les codes INSEE en dur de mémoire** : les résoudre via `https://geo.api.gouv.fr/communes?nom=<nom>&codeDepartement=57&fields=code,nom,centre`, puis les écrire dans un fichier de config `config/perimetre.yml`.

**Hors périmètre du premier jet :** MongoDB, bucket médias, NLP, DVF (de toute façon absent en Alsace-Moselle). Ils sont en **phase bonus** (§ 10).

---

## 2. Structure du dépôt à créer

```
HOMEPEDIA/
├── docker-compose.yml
├── .env                     # mots de passe et ports (non commité)
├── .env.example
├── config/
│   └── perimetre.yml        # liste des communes (code INSEE + nom)
├── mage/                    # projet Mage (monté dans le conteneur)
│   └── homepedia/
│       ├── pipelines/
│       ├── data_loaders/ transformers/ data_exporters/ custom/
│       └── dbt/homepedia_dbt/   # projet dbt (exécuté depuis Mage)
├── spark/
│   └── jobs/
│       ├── clean_cadastre.py
│       └── clean_cavites.py
├── docker/
│   └── mage/Dockerfile      # image Mage + Java + pyspark + client HDFS
├── sql/
│   └── init/00_init.sql     # extensions et schémas Postgres
└── docs/
    └── fiches-sources/      # 1 fiche par source (phase 1)
```

---

## 3. Phase 0 — Socle Docker minimal

**But :** avoir une base PostgreSQL + PostGIS qui tourne, et une structure de projet propre.

Tâches :
1. Créer l'arborescence ci-dessus (dossiers vides + `.gitignore` incluant `.env`, `data/`).
2. `docker-compose.yml` avec **un seul service** pour commencer : `postgres` (image `postgis/postgis`, version 16 ou 17 avec PostGIS 3.x), volume nommé, port `5432`.
3. `sql/init/00_init.sql` monté dans `/docker-entrypoint-initdb.d/` :
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   CREATE SCHEMA IF NOT EXISTS silver;
   CREATE SCHEMA IF NOT EXISTS gold;
   ```
4. `.env.example` avec `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB=homepedia`.

**Vérification :** `docker compose exec postgres psql -U $POSTGRES_USER -d homepedia -c "SELECT postgis_full_version();"` renvoie une version, et `\dn` liste `silver` et `gold`.

**À faire comprendre :** ce qu'est un conteneur/volume, pourquoi on sépare les schémas `silver` et `gold`, ce qu'ajoute PostGIS (type `geometry`, SRID).

---

## 4. Phase 1 — Explorer les sources à la main

**But :** comprendre la forme des données **avant** d'écrire le moindre pipeline.

Tâches :
1. Résoudre les codes INSEE du périmètre via `geo.api.gouv.fr` → écrire `config/perimetre.yml`.
2. Télécharger à la main (`curl`) le fichier parcelles d'**une** commune, le décompresser, l'inspecter avec `jq` :
   - nombre de features, liste des clés de `properties` (attendu : `id`, `commune`, `prefixe`, `section`, `numero`, `contenance`, `arpente`, `created`, `updated` — à confirmer),
   - type de géométrie (`Polygon` / `MultiPolygon`), système de coordonnées.
3. Interroger l'API Géorisques `cavites` pour la même commune (lire la doc Swagger pour les paramètres exacts : code INSEE, pagination) ; noter les champs utiles (identifiant, type de cavité, nom, coordonnées, fiabilité du repérage). Si 503 persistant : prendre l'export CSV de la BD Cavités.
4. Rédiger une fiche par source dans `docs/fiches-sources/` : URL, licence (Licence Ouverte Etalab 2.0), format, projection, clé d'identification, champs retenus, fréquence de mise à jour, pièges repérés.

**Vérification :** les deux fiches existent et l'utilisateur sait répondre à : « quelle est la clé d'une parcelle, et comment elle se décompose ? » (14 caractères : département 2 + commune 3 + préfixe 3 + section 2 + numéro 4).

**Pièges à signaler :** codes INSEE ≠ codes postaux ; zéros de tête perdus si on lit un code en entier ; un fichier GeoJSON « FeatureCollection » est **un seul gros objet JSON** (important pour Spark, voir phase 4).

---

## 5. Phase 2 — Mage : ingestion vers le disque local

**But :** premier pipeline orchestré, sans HDFS pour l'instant (on isole les difficultés).

Tâches :
1. Ajouter le service `mage` au compose : d'abord l'image officielle `mageai/mageai` (tag récent, à vérifier), port `6789`, volume `./mage:/home/src`, projet `homepedia`.
2. Créer le pipeline `ingest_bronze` avec les blocs :
   - `load_perimetre` (data loader) : lit `config/perimetre.yml`.
   - `fetch_cadastre` (data loader ou custom) : pour chaque commune, télécharge le `.json.gz` parcelles.
   - `to_jsonl_cadastre` (transformer) : **convertit la FeatureCollection en JSON Lines** (une feature par ligne), en ajoutant `_ingested_at` et `_source_url`.
   - `fetch_cavites` : appelle l'API (pagination gérée, pause entre appels, retries) ou lit l'export CSV ; écrit en JSON Lines.
   - `write_local` (data exporter) : écrit dans `data/bronze/<source>/dep=57/ingest_date=<AAAA-MM-JJ>/<insee>.jsonl`.
3. Rendre l'ingestion **idempotente** : relancer le pipeline le même jour réécrit les mêmes fichiers, sans doublons.

**Vérification :** les fichiers existent, `wc -l` = nombre de parcelles attendu, et un second lancement donne le même résultat.

**À faire comprendre :** blocs, DAG, passage de données entre blocs, triggers, logs dans l'UI ; pourquoi on garde le brut tel quel (rejouabilité) ; pourquoi on convertit en JSON Lines.

---

## 6. Phase 3 — HDFS : le data lake brut (bronze)

**But :** remplacer le disque local par HDFS.

Tâches :
1. Ajouter `namenode` et `datanode` au compose (image `apache/hadoop` version 3.x, cf. le `docker-compose` d'exemple de la doc Apache). Config minimale : `fs.defaultFS=hdfs://namenode:8020`, `dfs.replication=1` (un seul datanode). UI NameNode sur `9870`.
2. Créer l'arborescence : `hdfs dfs -mkdir -p /bronze/cadastre /bronze/cavites`.
3. Construire `docker/mage/Dockerfile` (base `mageai/mageai`) qui ajoute le paquet Python `hdfs` (client WebHDFS). Modifier l'exporter pour écrire dans `/bronze/<source>/dep=57/ingest_date=.../` via WebHDFS (`http://namenode:9870`).

**Vérification :** `hdfs dfs -ls -R /bronze` montre les fichiers ; l'UI 9870 (« Browse the file system ») aussi ; `hdfs dfs -cat ... | head -1` affiche une feature.

**Pièges :** WebHDFS redirige l'écriture vers le **datanode par son nom d'hôte** → tous les services doivent être sur le même réseau Docker ; conflit de port 9000 si un autre service (MinIO) l'utilise, d'où le choix de 8020 ; le « small files problem » (ne pas créer un fichier par parcelle).

**À faire comprendre :** NameNode vs DataNode, blocs de 128 Mo, réplication, pourquoi HDFS n'est pas une base de données.

---

## 7. Phase 4 — Spark : nettoyer et typer (bronze → silver)

**But :** lire le brut dans HDFS, le nettoyer, l'écrire dans PostgreSQL `silver`.

Tâches :
1. Ajouter `spark-master` (UI `8080`, port `7077`) et un `spark-worker` au compose (image officielle `apache/spark` 3.5.x ou 4.x). Choisir **une** version de Spark et s'y tenir partout.
2. Étendre `docker/mage/Dockerfile` : Java (JRE 17) + `pyspark` **à la même version exacte que le cluster**. Mage sera le *driver*, le cluster exécute.
3. `spark/jobs/clean_cadastre.py` :
   - lit `hdfs://namenode:8020/bronze/cadastre/dep=57/ingest_date=*/`,
   - aplatit `properties.*`, renomme en snake_case, caste (`contenance` → entier, dates → timestamp),
   - garde la géométrie en texte GeoJSON (`to_json(geometry)`),
   - dédoublonne sur `id` en gardant l'ingestion la plus récente,
   - écrit en JDBC dans `silver.parcelles` (mode `overwrite`), avec le driver `org.postgresql:postgresql` (via `spark.jars.packages`).
4. `spark/jobs/clean_cavites.py` : même logique → `silver.cavites` (identifiant, type, nom, code_insee, longitude, latitude, précision de repérage).
5. Jointure non spatiale pédagogique dans Spark : compter les cavités par `code_insee` et les parcelles par `commune`, écrire `silver.stats_communes_brutes`. (Le vrai croisement spatial se fait en PostGIS, phase 5.)
6. Bloc Mage `run_spark_clean` qui lance les deux jobs.

**Vérification :** l'UI Spark (8080) montre l'application terminée ; `SELECT count(*) FROM silver.parcelles;` = nombre de lignes JSONL ; aucune clé `id` en double.

**Pièges :** lire un GeoJSON non converti avec `multiLine=true` = un seul enregistrement géant non parallélisable ; `collect()` sur tout le dataset fait tomber le driver ; version pyspark ≠ version cluster → erreurs de sérialisation obscures.

**À faire comprendre :** évaluation paresseuse (transformations vs actions), partitions, driver vs executors, ce qu'est un *shuffle* et pourquoi un `groupBy` en provoque un.

---

## 8. Phase 5 — dbt : modèles gold, tests, lineage

**But :** transformer le silver en tables métier testées et documentées.

Tâches :
1. Installer `dbt-postgres` dans l'image Mage. Créer `mage/homepedia/dbt/homepedia_dbt` (`dbt init`), `profiles.yml` pointant sur `postgres:5432/homepedia`.
2. Déclarer les sources `silver.parcelles` et `silver.cavites` dans `models/sources.yml`.
3. Modèles **staging** (vues) : `stg_parcelles` (géométrie via `ST_SetSRID(ST_GeomFromGeoJSON(geometry), 4326)` puis `ST_Transform(..., 2154)` — Lambert-93, en mètres), `stg_cavites` (`ST_Transform(ST_SetSRID(ST_MakePoint(lon, lat), 4326), 2154)`).
4. Modèles **gold** (tables) :
   - `gold.parcelles_exposition_cavites` : par parcelle, `nb_cavites_200m`, `nb_cavites_500m`, `distance_cavite_la_plus_proche_m`, `classe_exposition` (`aucune` / `proximite` / `forte`), `surface_m2`, centroïde en `longitude` / `latitude` WGS84 (pour Superset). Utiliser `ST_DWithin` et un index GiST (via `post_hook`).
   - `gold.communes_synthese` : par commune, nb parcelles, nb cavités, % de parcelles exposées, surface médiane.
5. Tests YAML : `unique` + `not_null` sur les clés, `accepted_values` sur `classe_exposition`, `relationships` entre les deux modèles gold.
6. `dbt build` puis `dbt docs generate` ; montrer le graphe de lineage (`dbt docs serve`, port à exposer).
7. Bloc Mage (bloc dbt natif ou commande) qui lance `dbt build`.

**Vérification :** `dbt build` tout vert ; requête de contrôle : la parcelle la plus exposée de chaque commune ; le graphe de lineage montre `sources → staging → gold`.

**Pièges :** calculer des distances en degrés (SRID 4326) au lieu de mètres ; oublier l'index spatial (jointure lente) ; mettre de la logique métier dans Spark au lieu de dbt.

**À faire comprendre :** `ref()` et `source()`, matérialisations view/table, ce qu'est le lineage, différence ETL (Spark) / ELT (dbt).

---

## 9. Phase 6 — Superset : le premier tableau de bord

**But :** rendre le résultat lisible par un professionnel.

Tâches :
1. Ajouter `superset` au compose (image `apache/superset`, port `8088`), avec `SUPERSET_SECRET_KEY`, puis l'init : `superset db upgrade`, `superset fab create-admin`, `superset init`. (Superset utilise sa propre base de métadonnées : SQLite par défaut suffit pour le prototype.)
2. Connecter la base : `postgresql+psycopg2://user:pass@postgres:5432/homepedia`.
3. Créer les datasets sur `gold.parcelles_exposition_cavites` et `gold.communes_synthese`.
4. Dashboard « Cavités & parcelles — Moselle » :
   - carte deck.gl Scatter (centroïdes colorés par `classe_exposition`) ; configurer le fond de carte (clé Mapbox ou tuiles OSM selon ce que la version installée permet),
   - barres : % de parcelles exposées par commune,
   - Big Number : nombre total de parcelles en exposition forte,
   - filtre natif par commune.

**Vérification :** le dashboard s'affiche, le filtre commune agit sur les 3 graphiques.

**À faire comprendre :** base / dataset / chart / dashboard, SQL Lab, pourquoi on branche Superset sur le gold (pré-agrégé) et pas sur le bronze.

---

## 10. Phase 7 — Orchestration de bout en bout

1. Pipeline Mage `homepedia_full` : `ingest_bronze` → `run_spark_clean` → `dbt build`.
2. Trigger planifié hebdomadaire + trigger manuel.
3. Ajouter une commune au `perimetre.yml`, relancer, constater qu'elle apparaît dans Superset **sans rien toucher d'autre**.

**Vérification :** ce dernier test est le critère de réussite du premier jet.

---

## 11. Phase bonus — MongoDB et bucket médias

À ne lancer qu'une fois la phase 7 validée.

- **MongoDB** : service `mongo` (port 27017). Stocker dans une collection `cavites_brutes` les réponses JSON complètes de l'API Géorisques (avec leurs champs imbriqués), écrites par Spark via le connecteur MongoDB Spark. Faire une agrégation simple (`$group` par type de cavité). Constater que Superset ne se connecte pas nativement à MongoDB → discuter des options (Trino, ou pousser les agrégats dans Postgres).
- **Bucket médias** : service S3-compatible (MinIO, ou SeaweedFS/Garage si les images MinIO ne sont plus publiées — vérifier). Bucket `medias`. Bloc Mage qui télécharge un PDF de règlement (ex. un PPR ou une fiche) et le range sous `medias/pdf/<insee>/...`, avec la clé stockée dans une table Postgres.

---

## 12. Ressources machine et ports

| Service | Port hôte | RAM indicative |
|---|---|---|
| postgres | 5432 | 0,5 Go |
| mage | 6789 | 1–2 Go |
| namenode / datanode | 9870 (UI), 8020 (RPC interne) | 1–1,5 Go |
| spark-master / worker | 8080 (UI), 7077 | 2–3 Go |
| superset | 8088 | 1–1,5 Go |
| dbt docs | 8081 (au choix) | — |
| mongo (bonus) | 27017 | 0,5 Go |

Prévoir **8 Go minimum alloués à Docker**. Si la machine sature, n'allumer que les services de la phase en cours (`docker compose up <service>`), grâce à des *profiles* compose.

---

## 13. Définition de « terminé »

- [ ] `docker compose up` lance toute la stack sans intervention manuelle.
- [ ] Le pipeline Mage `homepedia_full` passe au vert.
- [ ] `dbt build` passe (tests compris) et le lineage est consultable.
- [ ] Le dashboard Superset montre carte + barres + chiffre clé, filtrables par commune.
- [ ] Ajouter une commune = modifier une ligne de config.
- [ ] Un `README.md` explique comment lancer, et où regarder à chaque étape (URLs des UIs).
- [ ] L'utilisateur sait expliquer le trajet d'une parcelle de la source au dashboard.
