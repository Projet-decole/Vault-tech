"""Bloc — Écrit les cavités (JSON Lines) dans la zone bronze de HDFS.

Arborescence : /bronze/cavites/dep=<dep>/ingest_date=<AAAA-MM-JJ>/departement-<dep>.jsonl
Idempotent : relancer le même jour vide puis réécrit le dossier du jour → pas de doublons.
(Le cadastre, beaucoup plus volumineux, est écrit en flux par le bloc ingest_cadastre.)
"""
import pandas as pd

from homepedia.utils.hdfs import client_hdfs, ecrire_jsonl, jour_ingestion, preparer_dossier

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def write_hdfs(cavites: pd.DataFrame, *args, **kwargs) -> None:
    client = client_hdfs()
    jour = jour_ingestion(kwargs)
    for (source, dep), groupe in cavites.groupby(['source', 'departement']):
        dossier = preparer_dossier(client, source, dep, jour)
        # Un fichier par département : pas un par cavité ("small files problem" de HDFS)
        for fichier, lignes in groupe.groupby('fichier'):
            ecrire_jsonl(client, f'{dossier}/{fichier}.jsonl', list(lignes['ligne']))
            print(f'hdfs://{dossier}/{fichier}.jsonl : {len(lignes)} lignes')
