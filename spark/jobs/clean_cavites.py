"""Job Spark — bronze → silver : cavités souterraines (BD Cavités BRGM).

Lit   hdfs://namenode:8020/bronze/cavites/dep=*/ingest_date=*/*.jsonl  (1 ligne = 1 cavité, champs du CSV)
Écrit silver.cavites dans PostgreSQL

Coordonnées (voir docs/fiches-sources/cavites-bdcavites.md) : les colonnes brutes mélangent plusieurs
systèmes. On produit x, y + srid (code du système) ; la conversion en GPS se fera dans PostGIS (phase 5).
"""
from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql.window import Window

from commun import lire_bronze, ecrire_table, session

# On ne déclare que les champs utiles : les autres (e-mails d'agents, validation...) sont ignorés.
CHAMPS = ['numCavite', 'nomCavite', 'typeCavite', 'typeCaviteAppauvri', 'natureCavite', 'statut',
          'numInsee', 'positionnement', 'precisionXY', 'reperageGeographique', 'confidentialite',
          'lambertOuvrage', 'xOuvrage', 'yOuvrage', 'xouvl2e', 'youvl2e', 'dateMajCavite',
          'commentaires', '_ingested_at', '_source_url']
SCHEMA = T.StructType([T.StructField(c, T.StringType()) for c in CHAMPS])


def vide_en_null(col: str):
    """Le CSV source met "" pour une valeur absente : on la remplace par un vrai NULL."""
    return F.when(F.trim(F.col(col)) == '', None).otherwise(F.trim(F.col(col)))


def main():
    spark = session('clean_cavites')
    brut = lire_bronze(spark, 'cavites', SCHEMA)

    # Règle de choix des coordonnées :
    #   1. colonnes harmonisées xouvl2e/youvl2e (Lambert II étendu, EPSG:27572) si présentes
    #   2. sinon, si lambertOuvrage = 6, xOuvrage/yOuvrage sont déjà en GPS (EPSG:4326)
    #   3. sinon pas de coordonnées (cavités confidentielles)
    a_l2e = vide_en_null('xouvl2e').isNotNull()
    en_gps = vide_en_null('lambertOuvrage') == '6'

    cavites = brut.select(
        F.col('numCavite').alias('id_cavite'),
        vide_en_null('nomCavite').alias('nom'),
        vide_en_null('typeCavite').alias('type_cavite'),
        vide_en_null('typeCaviteAppauvri').alias('type_cavite_code'),  # sans accents : pratique pour filtrer
        vide_en_null('natureCavite').alias('nature'),
        vide_en_null('statut').alias('statut'),
        F.col('numInsee').alias('code_insee'),
        vide_en_null('positionnement').alias('positionnement'),
        vide_en_null('precisionXY').cast('int').alias('precision_xy_m'),
        vide_en_null('reperageGeographique').alias('reperage'),
        vide_en_null('confidentialite').alias('confidentialite'),
        F.when(a_l2e, vide_en_null('xouvl2e')).when(en_gps, vide_en_null('xOuvrage')).cast('double').alias('x'),
        F.when(a_l2e, vide_en_null('youvl2e')).when(en_gps, vide_en_null('yOuvrage')).cast('double').alias('y'),
        F.when(a_l2e, F.lit(27572)).when(en_gps, F.lit(4326)).alias('srid'),
        F.to_date(vide_en_null('dateMajCavite')).alias('date_maj'),
        vide_en_null('commentaires').alias('commentaires'),
        F.col('dep').alias('departement'),
        F.to_date('ingest_date').alias('ingest_date'),
        F.to_timestamp('_ingested_at').alias('ingested_at'),
        F.col('_source_url').alias('source_url'),
    )

    # Dédoublonnage : dernière ingestion de chaque cavité (même principe que pour les parcelles)
    recente_d_abord = Window.partitionBy('id_cavite').orderBy(F.col('ingest_date').desc(), F.col('ingested_at').desc())
    cavites = (cavites
               .withColumn('_rang', F.row_number().over(recente_d_abord))
               .filter('_rang = 1')
               .drop('_rang')
               .cache())

    ecrire_table(cavites, 'silver.cavites')
    print(f'silver.cavites écrite : {cavites.count()} cavités, '
          f'dont {cavites.filter("srid IS NULL").count()} sans coordonnées')
    spark.stop()


if __name__ == '__main__':
    main()
