"""Lance un job Spark (spark/jobs/*.py) sur le cluster, depuis Mage.

Mage devient le "driver" : il lit le script, découpe le travail et l'envoie aux executors
du spark-worker. Les logs du job s'affichent dans les logs du bloc Mage.
"""
import os
import subprocess

import requests

DOSSIER_JOBS = '/spark/jobs'  # monté depuis ./spark/jobs (docker-compose)
UI_MASTER = 'http://spark-master:8080/json/'  # état du cluster, en JSON
DELAI_MAX_S = 15 * 60  # un job de notre taille prend ~30 s : au-delà de 15 min, c'est qu'il est bloqué
# pyspark vit dans un virtualenv séparé (voir docker/mage/Dockerfile : pourquoi Mage ne doit pas le voir)
VENV_PYSPARK = '/opt/pyspark'

CONF = {
    # Adresse du master (le "bureau d'embauche")
    'spark.master': 'spark://spark-master:7077',
    # Les executors doivent pouvoir rappeler le driver : on leur donne le nom du conteneur Mage
    'spark.driver.host': 'mage',
    'spark.driver.bindAddress': '0.0.0.0',
    # Ressources (dimensionnées pour le Rhône entier, ~1,9 M parcelles / ~1 Go de JSON) :
    # 1 executor de 4 cœurs / 2 Go sur le worker (qui en offre 3 Go) ; le driver (dans Mage) reste léger
    'spark.driver.memory': '1g',
    'spark.executor.memory': '2g',
    'spark.cores.max': '4',
    # Nombre de morceaux après un shuffle (200 par défaut : trop pour notre volume, 16 = 4 par cœur)
    'spark.sql.shuffle.partitions': '16',
    # Bibliothèques Java téléchargées automatiquement depuis Maven Central au 1er lancement :
    #   - pilote JDBC PostgreSQL
    #   - connecteur MongoDB pour Spark (Scala 2.13, génération Spark 4) — phase bonus
    'spark.jars.packages': 'org.postgresql:postgresql:42.7.13,'
                           'org.mongodb.spark:mongo-spark-connector_2.13:11.1.0',
    # Ne pas deviner le type des dossiers "dep=57" : 57 doit rester un texte, pas un nombre
    'spark.sql.sources.partitionColumnTypeInference.enabled': 'false',
    # HDFS : contacter le DataNode par son nom "datanode" (cohérent avec docker/hadoop/hadoop.env)
    'spark.hadoop.dfs.client.use.datanode.hostname': 'true',
}


def verifier_workers() -> None:
    """Échoue tout de suite si le master n'a aucun worker, au lieu d'attendre indéfiniment.

    Cas vécu : après une mise en veille de la machine, le master "oublie" le worker (plus de
    nouvelles pendant 60 s) mais le worker ne s'en rend pas compte → le job reste en WAITING.
    """
    etat = requests.get(UI_MASTER, timeout=10).json()
    if etat.get('aliveworkers', 0) < 1:
        raise RuntimeError(
            'Aucun worker Spark enregistré auprès du master (voir http://localhost:8080). '
            'Relancer le worker : docker compose restart spark-worker'
        )
    print(f"Cluster Spark : {etat['aliveworkers']} worker(s), {etat['cores']} cœurs, {etat['memory']} Mo")


def spark_submit(script: str) -> None:
    verifier_workers()
    commande = [f'{VENV_PYSPARK}/bin/spark-submit']
    for cle, valeur in CONF.items():
        commande += ['--conf', f'{cle}={valeur}']
    commande.append(f'{DOSSIER_JOBS}/{script}')

    # Le script du job (le driver) s'exécute avec le Python du virtualenv, qui connaît pyspark.
    # (Pas PYSPARK_PYTHON : il viserait aussi les executors, sur le worker, où ce chemin n'existe pas.)
    env = {**os.environ, 'PYSPARK_DRIVER_PYTHON': f'{VENV_PYSPARK}/bin/python'}

    print('$', ' '.join(commande))
    # Les logs de Spark remontent en direct dans Mage ; une erreur Spark fait échouer le bloc,
    # de même qu'un dépassement du délai maximum (subprocess.TimeoutExpired)
    subprocess.run(commande, check=True, env=env, timeout=DELAI_MAX_S)
