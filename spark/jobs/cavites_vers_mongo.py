"""Job Spark — bronze → MongoDB : fiche COMPLÈTE de chaque cavité, en document imbriqué.

Lit    hdfs://namenode:8020/bronze/cavites/  (tous les champs du CSV BRGM, dernière ingestion)
       + silver.cavites (PostgreSQL) pour la position, convertie en GPS par PostGIS
Écrit  MongoDB homepedia.cavites_fiches : un document par cavité, _id = numCavite

Différence avec silver.cavites (Postgres) : ici on garde TOUS les champs utiles, regroupés en
sous-documents (identification, localisation, description, historique, source), plus le texte
libre. C'est la "fiche" consultable ; Postgres garde les colonnes utiles aux calculs.
"""
from pyspark.sql import functions as F
from pyspark.sql.window import Window

from commun import lire_bronze, lire_requete, session, uri_mongo


def texte(col: str):
    """Chaîne nettoyée ; "" (valeur absente dans le CSV) devient null."""
    return F.when(F.trim(F.col(col)) == '', None).otherwise(F.trim(F.col(col)))


def main():
    spark = session('cavites_vers_mongo')

    # Tous les champs sont du texte dans le CSV d'origine : Spark les lit tels quels
    brut = lire_bronze(spark, 'cavites')

    # Dernière ingestion de chaque cavité (même règle que pour le silver)
    recente = Window.partitionBy('numCavite').orderBy(F.col('ingest_date').desc(), F.col('_ingested_at').desc())
    brut = brut.withColumn('_rang', F.row_number().over(recente)).filter('_rang = 1')

    # Position GPS calculée par PostGIS à partir de silver.cavites (x, y dans le système "srid").
    # La requête s'exécute dans Postgres. Même formule et même règle de fiabilité que dbt (stg_cavites),
    # mais sans dépendre de dbt : cette branche peut tourner juste après le nettoyage Spark.
    positions = lire_requete(spark, """
        select id_cavite,
               ST_X(ST_Transform(ST_SetSRID(ST_MakePoint(x, y), srid), 4326)) as lon,
               ST_Y(ST_Transform(ST_SetSRID(ST_MakePoint(x, y), srid), 4326)) as lat,
               positionnement is distinct from 'centroide de commune'       as localisation_fiable
        from silver.cavites
        where srid is not null
    """)

    docs = brut.join(positions, brut.numCavite == positions.id_cavite, 'left').select(
        F.col('numCavite').alias('_id'),   # _id = clé primaire d'un document MongoDB
        F.struct(
            F.col('numCavite').alias('numero'),
            texte('id').alias('id_brgm'),
            texte('nomCavite').alias('nom'),
            texte('typeCavite').alias('type'),
            texte('natureCavite').alias('nature'),
            texte('statut').alias('statut'),
            texte('indiceBSS').alias('indice_bss'),
            texte('designationBSS').alias('designation_bss'),
        ).alias('identification'),
        F.struct(
            F.col('numInsee').alias('code_insee'),
            F.col('dep').alias('departement'),
            texte('reperageGeographique').alias('reperage'),
            texte('positionnement').alias('positionnement'),
            texte('precisionXY').cast('int').alias('precision_m'),
            texte('sourceCoordonnees').alias('source_coordonnees'),
            texte('zOuvrage').cast('double').alias('altitude_m'),
            F.col('localisation_fiable'),
            # Point GeoJSON [longitude, latitude] : MongoDB sait l'indexer (index "2dsphere")
            F.when(F.col('lon').isNotNull(), F.struct(
                F.lit('Point').alias('type'),
                F.array('lon', 'lat').alias('coordinates'),
            )).alias('point'),
        ).alias('localisation'),
        F.struct(
            texte('commentaires').alias('commentaires'),
            texte('caviteAssociee').alias('cavite_associee'),
            texte('confidentialite').alias('confidentialite'),
            texte('raisonConfidentialite').alias('raison_confidentialite'),
        ).alias('description'),
        F.struct(
            texte('auteurDescription').alias('auteur'),
            F.to_date(texte('dateValidite')).alias('date_validite'),
            F.to_date(texte('dateMajCavite')).alias('date_maj'),
            texte('statutValidation').alias('statut_validation'),
        ).alias('historique'),
        # Champs écartés : cUserSaisie, userValidation... (e-mails d'agents = données personnelles)
        F.struct(
            F.col('_source_url').alias('url'),
            F.to_timestamp('_ingested_at').alias('ingere_le'),
            F.to_date('ingest_date').alias('ingest_date'),
        ).alias('source'),
    )

    # overwrite : la collection est vidée puis réécrite (les index sont recréés ensuite par Mage)
    (docs.write.format('mongodb')
         .mode('overwrite')
         .option('connection.uri', uri_mongo())
         .option('database', 'homepedia')
         .option('collection', 'cavites_fiches')
         .save())

    print(f'MongoDB homepedia.cavites_fiches écrite : {docs.count()} fiches')
    spark.stop()


if __name__ == '__main__':
    main()
