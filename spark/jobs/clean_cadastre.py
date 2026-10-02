"""Job Spark — bronze → silver : parcelles cadastrales.

Lit   hdfs://namenode:8020/bronze/cadastre/dep=*/<dernière ingest_date>/*.jsonl  (1 ligne = 1 parcelle GeoJSON)
Écrit silver.parcelles dans PostgreSQL (1 ligne par parcelle, colonnes typées)
"""
from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql.window import Window

from commun import lire_bronze, ecrire_table, session

# Schéma explicite : plus rapide que de laisser Spark le deviner (il relirait toutes les données),
# et on contrôle les types (codes = texte, pour garder les zéros de tête).
SCHEMA = T.StructType([
    T.StructField('id', T.StringType()),
    # StringType sur un objet JSON → Spark garde le texte brut de la géométrie (GeoJSON).
    # Pratique : Polygon et MultiPolygon n'ont pas la même structure imbriquée.
    T.StructField('geometry', T.StringType()),
    T.StructField('properties', T.StructType([
        T.StructField('id', T.StringType()),
        T.StructField('commune', T.StringType()),
        T.StructField('prefixe', T.StringType()),
        T.StructField('section', T.StringType()),
        T.StructField('numero', T.StringType()),
        T.StructField('contenance', T.LongType()),
        T.StructField('arpente', T.BooleanType()),
        T.StructField('created', T.StringType()),
        T.StructField('updated', T.StringType()),
    ])),
    T.StructField('_ingested_at', T.StringType()),
    T.StructField('_source_url', T.StringType()),
])


def main():
    spark = session('clean_cadastre')

    # --- Lecture (transformation : rien n'est encore lu à ce stade) ---
    # Dernière ingestion de chaque département seulement (voir commun.lire_bronze) ;
    # les dossiers dep=57/ingest_date=... deviennent des colonnes "dep" et "ingest_date".
    brut = lire_bronze(spark, 'cadastre', SCHEMA)

    # --- Mise à plat et typage ---
    parcelles = brut.select(
        F.col('properties.id').alias('id_parcelle'),
        F.col('properties.commune').alias('code_insee'),
        F.col('properties.prefixe').alias('prefixe'),
        F.col('properties.section').alias('section'),
        F.col('properties.numero').alias('numero'),
        F.col('properties.contenance').cast('int').alias('contenance_m2'),
        F.col('properties.arpente').alias('arpente'),
        F.to_date('properties.created').alias('date_creation'),
        F.to_date('properties.updated').alias('date_maj'),
        F.col('geometry').alias('geometrie_geojson'),  # reste en texte GeoJSON (WGS84) ; PostGIS s'en charge en phase 5
        F.col('dep').alias('departement'),
        F.to_date('ingest_date').alias('ingest_date'),
        F.to_timestamp('_ingested_at').alias('ingested_at'),
        F.col('_source_url').alias('source_url'),
    )

    # --- Dédoublonnage : si une parcelle a été ingérée plusieurs jours, on garde la plus récente ---
    # Window = "pour chaque id_parcelle, numérote les lignes de la plus récente à la plus ancienne".
    # Provoque un SHUFFLE : Spark doit regrouper sur la même machine toutes les lignes d'un même id.
    recente_d_abord = Window.partitionBy('id_parcelle').orderBy(F.col('ingest_date').desc(), F.col('ingested_at').desc())
    parcelles = (parcelles
                 .withColumn('_rang', F.row_number().over(recente_d_abord))
                 .filter('_rang = 1')
                 .drop('_rang')
                 # cache : garde le résultat en mémoire des executors après le 1er calcul.
                 # Sans ça, le count() plus bas referait TOUT (lecture HDFS, shuffle...).
                 .cache())

    # --- Écriture (ACTION : c'est ici que Spark exécute réellement tout ce qui précède) ---
    ecrire_table(parcelles, 'silver.parcelles')

    # 2e action, servie par le cache. count() renvoie un simple nombre au driver
    # (≠ collect(), qui rapatrierait toutes les lignes et ferait tomber le driver sur un gros volume).
    print(f'silver.parcelles écrite : {parcelles.count()} parcelles')
    spark.stop()


if __name__ == '__main__':
    main()
