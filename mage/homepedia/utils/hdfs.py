"""Écriture dans la zone bronze de HDFS (via WebHDFS), partagée par les blocs d'ingestion."""
import os
from datetime import date

from hdfs import InsecureClient


def client_hdfs() -> InsecureClient:
    # Client WebHDFS : parle au NameNode en HTTP ("Insecure" = sans authentification Kerberos)
    return InsecureClient(os.environ['HDFS_WEB_URL'], user=os.environ['HDFS_USER'])


def jour_ingestion(kwargs: dict) -> str:
    """Date du run : fournie par Mage (trigger planifié), sinon aujourd'hui."""
    execution = kwargs.get('execution_date')
    return (execution.date() if execution else date.today()).isoformat()


def preparer_dossier(client: InsecureClient, source: str, dep: str, jour: str) -> str:
    """Vide puis recrée /bronze/<source>/dep=<dep>/ingest_date=<jour> (idempotence : relancer
    le même jour réécrit les mêmes fichiers, sans doublons). Renvoie le chemin du dossier."""
    dossier = f'/bronze/{source}/dep={dep}/ingest_date={jour}'
    client.delete(dossier, recursive=True)
    client.makedirs(dossier)
    return dossier


def ecrire_jsonl(client: InsecureClient, chemin: str, lignes: list) -> None:
    """Écrit une liste de lignes JSON (texte) dans un fichier HDFS.

    On encode NOUS-MÊMES en octets : avec encoding='utf-8', la bibliothèque hdfs encode et
    envoie caractère par caractère (66 millions de morceaux → ~8 min au lieu de ~2 s).
    """
    client.write(chemin, data=('\n'.join(lignes) + '\n').encode('utf-8'), overwrite=True)
