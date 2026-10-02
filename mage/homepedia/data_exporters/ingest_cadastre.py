"""Bloc — Cadastre : télécharge, convertit en JSON Lines et écrit dans HDFS, commune par commune (en FLUX).

Remplace les blocs fetch_cadastre → to_jsonl_cadastre → write_hdfs du premier jet, qui se passaient
TOUTES les données en mémoire : impossible à l'échelle d'un département (~1 Go de GeoJSON).
Ici, une seule commune est en mémoire à la fois ; le bloc ne renvoie qu'un petit résumé.

HDFS : /bronze/cadastre/dep=<dep>/ingest_date=<jour>/<insee>.jsonl  (une parcelle = une ligne)
"""
import gzip
import json
import time
from datetime import datetime, timezone

import pandas as pd
import requests

from homepedia.utils.hdfs import client_hdfs, ecrire_jsonl, jour_ingestion, preparer_dossier
from homepedia.utils.http import telecharger

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

# 'latest' redirige vers le dernier millésime daté (ex. .../2026-06-01/...)
URL_MODELE = ('https://cadastre.data.gouv.fr/data/etalab-cadastre/latest/geojson/'
              'communes/{dep}/{insee}/cadastre-{insee}-parcelles.json.gz')


@data_exporter
def ingest_cadastre(perimetre: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
    client = client_hdfs()
    jour = jour_ingestion(kwargs)
    resume = []

    for dep, communes in perimetre.groupby('departement'):
        dossier = preparer_dossier(client, 'cadastre', dep, jour)
        debut = time.time()
        for n, commune in enumerate(communes.itertuples(), start=1):
            url = URL_MODELE.format(dep=dep, insee=commune.insee)
            try:
                r = telecharger(url)
            except requests.HTTPError as erreur:
                # Ex. commune nouvelle absente du millésime cadastral : on signale et on continue
                if erreur.response is not None and erreur.response.status_code == 404:
                    print(f'  ABSENTE du cadastre : {commune.nom} ({commune.insee})')
                    resume.append({'insee': commune.insee, 'nb_parcelles': 0, 'statut': 'absente'})
                    continue
                raise

            contenu = gzip.decompress(r.content) if r.content[:2] == b'\x1f\x8b' else r.content
            ingere_le = datetime.now(timezone.utc).isoformat(timespec='seconds')
            lignes = []
            # FeatureCollection → une Feature par ligne + métadonnées d'ingestion
            for feature in json.loads(contenu)['features']:
                feature['_ingested_at'] = ingere_le
                feature['_source_url'] = r.url   # URL finale : trace le millésime téléchargé
                lignes.append(json.dumps(feature, ensure_ascii=False))
            ecrire_jsonl(client, f'{dossier}/{commune.insee}.jsonl', lignes)
            resume.append({'insee': commune.insee, 'nb_parcelles': len(lignes), 'statut': 'ok'})

            if n % 25 == 0 or n == len(communes):   # un point d'étape toutes les 25 communes
                print(f'  dép. {dep} : {n}/{len(communes)} communes ({time.time() - debut:.0f} s)')
            del contenu, lignes     # libère la mémoire avant la commune suivante
            time.sleep(0.2)         # politesse envers le serveur

    df = pd.DataFrame(resume)
    print(f"Cadastre : {df['nb_parcelles'].sum()} parcelles, "
          f"{(df['statut'] == 'absente').sum()} commune(s) absente(s) du cadastre")
    return df


@test
def test_communes_ingerees(df, *args) -> None:
    assert (df['statut'] == 'ok').any(), 'Aucune commune ingérée'
    # Quelques absences sont normales (communes nouvelles) ; beaucoup = problème de source
    assert (df['statut'] == 'absente').mean() < 0.05, 'Plus de 5 % des communes absentes du cadastre'
