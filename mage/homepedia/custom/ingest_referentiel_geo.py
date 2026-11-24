"""Bloc — Télécharge le référentiel géographique de la France et l'écrit dans la zone bronze de HDFS.

Deux sources, toutes deux nationales (dossier dep=FR) :
  - COG INSEE (Code officiel géographique) : la liste officielle des régions, départements et communes,
    avec les anciennes communes (fusionnées) et leur commune actuelle. Repris du travail de Frank
    (branche feature/indicateurs-prix-loyers du repo de l'école, ingestion/sources/cog_insee.py).
  - Contours administratifs Etalab (dérivés d'ADMIN EXPRESS, IGN), simplifiés à 100 m :
    les polygones nécessaires aux cartes choroplèthes (une couleur par territoire).

Arborescence :
  /bronze/cog/dep=FR/ingest_date=<jour>/{region,departement,commune}.jsonl       (1 ligne = 1 ligne du CSV)
  /bronze/contours/dep=FR/ingest_date=<jour>/{regions,departements,communes}.jsonl (1 ligne = 1 territoire)
Un champ "niveau" dans chaque ligne dit de quel fichier elle vient (Spark lit tout le dossier d'un coup).
"""
import csv
import io
import json
from datetime import datetime, timezone

from homepedia.utils.hdfs import client_hdfs, ecrire_jsonl, jour_ingestion, preparer_dossier
from homepedia.utils.http import telecharger

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom

# Le COG change d'identifiant de page à chaque millésime (voir https://www.insee.fr/fr/information/8740222)
COG_ANNEE, COG_PAGE = 2026, '8740222'
COG_URL = 'https://www.insee.fr/fr/statistiques/fichier/{page}/v_{nom}_{annee}.csv'
COG_FICHIERS = ['region', 'departement', 'commune']

CONTOURS_URL = 'https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/latest/geojson/{nom}-100m.geojson'
CONTOURS_FICHIERS = ['regions', 'departements', 'communes']


@custom
def ingest_referentiel_geo(*args, **kwargs) -> None:
    client = client_hdfs()
    jour = jour_ingestion(kwargs)
    ingere_le = datetime.now(timezone.utc).isoformat(timespec='seconds')

    dossier = preparer_dossier(client, 'cog', 'FR', jour)
    for nom in COG_FICHIERS:
        r = telecharger(COG_URL.format(page=COG_PAGE, nom=nom, annee=COG_ANNEE))
        # dtype texte partout : les codes ont des zéros en tête ("01") et des lettres ("2A")
        lecteur = csv.DictReader(io.StringIO(r.content.decode('utf-8-sig'), newline=''))
        lignes = [json.dumps({**ligne, 'niveau': nom, 'millesime': COG_ANNEE,
                              '_ingested_at': ingere_le, '_source_url': r.url}, ensure_ascii=False)
                  for ligne in lecteur]
        ecrire_jsonl(client, f'{dossier}/{nom}.jsonl', lignes)
        print(f'COG {nom} : {len(lignes)} lignes → hdfs://{dossier}/{nom}.jsonl')

    dossier = preparer_dossier(client, 'contours', 'FR', jour)
    for nom in CONTOURS_FICHIERS:
        r = telecharger(CONTOURS_URL.format(nom=nom), timeout_s=300)
        # Une FeatureCollection est UN seul objet JSON : Spark ne saurait pas la découper.
        # On la passe en JSON Lines (un territoire par ligne), comme le cadastre.
        lignes = [json.dumps({**f['properties'], 'niveau': nom,
                              'geometrie_geojson': json.dumps(f['geometry']),
                              '_ingested_at': ingere_le, '_source_url': r.url}, ensure_ascii=False)
                  for f in r.json()['features']]
        ecrire_jsonl(client, f'{dossier}/{nom}.jsonl', lignes)
        print(f'Contours {nom} : {len(lignes)} territoires → hdfs://{dossier}/{nom}.jsonl')
