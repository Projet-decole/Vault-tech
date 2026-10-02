"""Bloc 4 — Télécharge l'inventaire BRGM des cavités (CSV départemental) et le passe en JSON Lines.

Source : export CSV Géorisques (l'API officielle était en 503 au 2026-09-25).
Voir docs/fiches-sources/cavites-bdcavites.md.
On garde TOUT le département (pas de filtre par commune) : une cavité juste de l'autre
côté d'une limite communale peut être proche d'une parcelle du périmètre.
"""
import csv
import io
import json
from datetime import datetime, timezone

import pandas as pd

from homepedia.utils.http import telecharger

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

URL_MODELE = 'https://www.georisques.gouv.fr/webappReport/ws/cavites/departements/{dep}/fiches.csv?'


@data_loader
def fetch_cavites(perimetre: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
    ingere_le = datetime.now(timezone.utc).isoformat(timespec='seconds')
    lignes = []
    for dep in perimetre['departement'].unique():
        url = URL_MODELE.format(dep=dep)
        r = telecharger(url)
        # utf-8-sig : retire le BOM en tête de fichier (sinon 1re colonne = '﻿id')
        texte = r.content.decode('utf-8-sig')
        # Le module csv gère les retours à la ligne à l'intérieur des guillemets
        lecteur = csv.DictReader(io.StringIO(texte, newline=''), delimiter=';')
        nb = 0
        for cavite in lecteur:
            cavite.pop('', None)  # colonne vide créée par le ';' en fin de ligne
            cavite['_ingested_at'] = ingere_le
            cavite['_source_url'] = r.url
            lignes.append({
                'source': 'cavites',
                'departement': dep,
                'fichier': f'departement-{dep}',  # → departement-57.jsonl
                'ligne': json.dumps(cavite, ensure_ascii=False),
            })
            nb += 1
        print(f'Département {dep} : {nb} cavités — {url}')
    return pd.DataFrame(lignes)


@test
def test_cavites(df, *args) -> None:
    assert len(df) > 0, 'Aucune cavité téléchargée'
    ids = df['ligne'].map(lambda l: json.loads(l)['numCavite'])
    assert ids.is_unique, 'numCavite en double'
