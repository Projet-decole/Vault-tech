"""Fonctions partagées par les jobs Spark HOMEPEDIA.

Les jobs sont lancés par Mage avec spark-submit : le driver tourne dans le conteneur Mage,
les calculs sur le cluster (spark-master / spark-worker).
"""
import os

from pyspark.sql import DataFrame, SparkSession

HDFS = 'hdfs://namenode:8020'
# reWriteBatchedInserts : le pilote regroupe les INSERT d'un paquet en une seule requête (bien plus rapide)
JDBC_URL = 'jdbc:postgresql://postgres:5432/{db}?reWriteBatchedInserts=true'


def session(nom_app: str) -> SparkSession:
    """Ouvre (ou récupère) la session Spark configurée par spark-submit."""
    spark = SparkSession.builder.appName(nom_app).getOrCreate()
    spark.sparkContext.setLogLevel('WARN')  # moins de bruit dans les logs Mage
    return spark


def _options_jdbc() -> dict:
    # Identifiants lus dans l'environnement (fichier .env chargé par docker-compose)
    return {
        'url': JDBC_URL.format(db=os.environ['POSTGRES_DB']),
        'user': os.environ['POSTGRES_USER'],
        'password': os.environ['POSTGRES_PASSWORD'],
        'driver': 'org.postgresql.Driver',
    }


def ecrire_table(df: DataFrame, table: str) -> None:
    """Remplace le contenu d'une table Postgres (ex. 'silver.parcelles')."""
    (df.write.format('jdbc')
       .options(**_options_jdbc())
       .option('dbtable', table)
       # overwrite + truncate : vide la table au lieu de la supprimer/recréer.
       # Indispensable dès la phase 5 : les vues dbt qui dépendent de la table empêcheraient un DROP.
       .option('truncate', 'true')
       # Envoi par paquets de 10 000 lignes, sur 4 connexions Postgres en parallèle
       .option('batchsize', 10000)
       .option('numPartitions', 4)
       .mode('overwrite')
       .save())


def chemins_derniere_ingestion(spark: SparkSession, source: str) -> list:
    """Pour chaque département de /bronze/<source>, le chemin de la DERNIÈRE ingestion seulement.

    HDFS garde l'historique (une ingest_date par exécution) : tout relire à chaque fois coûterait
    de plus en plus cher (1 Go de plus chaque semaine pour le Rhône). On liste les dossiers
    (opération sur le "sommaire" du NameNode, sans lire les données) et on ne garde que le plus récent.
    """
    jvm = spark.sparkContext._jvm   # accès aux classes Java d'Hadoop depuis Python
    racine = jvm.org.apache.hadoop.fs.Path(f'{HDFS}/bronze/{source}')
    fs = racine.getFileSystem(spark.sparkContext._jsc.hadoopConfiguration())
    chemins = []
    for dossier_dep in fs.listStatus(racine):                      # dep=57, dep=69...
        dates = sorted(s.getPath().getName() for s in fs.listStatus(dossier_dep.getPath())
                       if s.getPath().getName().startswith('ingest_date='))
        if dates:
            chemins.append(f'{dossier_dep.getPath().toString()}/{dates[-1]}')
    print(f'{source} : lecture de {chemins}')
    return chemins


def lire_bronze(spark: SparkSession, source: str, schema=None) -> DataFrame:
    """Lit la dernière ingestion de chaque département ; les dossiers dep=/ingest_date= deviennent
    des colonnes grâce à basePath."""
    lecteur = spark.read.option('basePath', f'{HDFS}/bronze/{source}')
    if schema is not None:
        lecteur = lecteur.schema(schema)
    return lecteur.json(chemins_derniere_ingestion(spark, source))


def lire_table(spark: SparkSession, table: str) -> DataFrame:
    return spark.read.format('jdbc').options(**_options_jdbc()).option('dbtable', table).load()


def lire_requete(spark: SparkSession, sql: str) -> DataFrame:
    """Résultat d'une requête SQL exécutée PAR Postgres (utile pour profiter de PostGIS)."""
    return spark.read.format('jdbc').options(**_options_jdbc()).option('query', sql).load()


def uri_mongo() -> str:
    # Identifiants lus dans l'environnement (fichier .env) ; authSource=admin : le compte root vit dans "admin"
    return (f"mongodb://{os.environ['MONGO_ROOT_USER']}:{os.environ['MONGO_ROOT_PASSWORD']}"
            f"@mongo:27017/?authSource=admin")
