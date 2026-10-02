"""Bloc 1 — Construit la liste des communes à traiter à partir de config/perimetre.yml.

Deux façons de déclarer des communes (cumulables) :
  - "communes"     : une par une (code INSEE + nom) ;
  - "departements" : toutes les communes d'un département, lues sur geo.api.gouv.fr.
"""
import os

import pandas as pd
import yaml

from homepedia.utils.http import telecharger

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

GEO_API = ('https://geo.api.gouv.fr/communes?codeDepartement={dep}'
           '&type=commune-actuelle,arrondissement-municipal&fields=code,nom,codeParent')


@data_loader
def load_perimetre(*args, **kwargs) -> pd.DataFrame:
    # Chemin fourni par docker-compose (variable d'environnement)
    with open(os.environ['HOMEPEDIA_CONFIG'], encoding='utf-8') as f:
        conf = yaml.safe_load(f)

    communes = [{'insee': str(c['insee']), 'nom': c['nom']} for c in conf.get('communes') or []]
    for dep in conf.get('departements') or []:
        communes += communes_du_departement(str(dep))

    # dtype=str : les codes INSEE restent du texte (zéros de tête conservés)
    df = pd.DataFrame(communes, dtype=str)
    # Doublon (commune listée à l'unité ET via son département) : on garde la 1re occurrence
    df = df.drop_duplicates(subset='insee', keep='first').reset_index(drop=True)
    df['departement'] = df['insee'].map(departement_du_code_insee)
    print(f"{len(df)} communes dans le périmètre : {df['departement'].value_counts().to_dict()}")
    return df


def communes_du_departement(dep: str) -> list:
    """Toutes les communes d'un département, avec les ARRONDISSEMENTS à la place de Paris / Lyon / Marseille
    (le cadastre de ces villes n'existe que par arrondissement)."""
    liste = telecharger(GEO_API.format(dep=dep)).json()
    # Une ville "parente" d'arrondissements (ex. Lyon 69123) est remplacée par ses arrondissements
    villes_a_arrondissements = {c['codeParent'] for c in liste if c.get('codeParent')}
    return [{'insee': c['code'], 'nom': c['nom']} for c in liste if c['code'] not in villes_a_arrondissements]


def departement_du_code_insee(insee: str) -> str:
    """Règle officielle : 2 premiers caractères (01..95, 2A, 2B), 3 pour l'outre-mer (971..976)."""
    return insee[:3] if insee.startswith('97') else insee[:2]


@test
def test_codes_insee(df, *args) -> None:
    assert len(df) > 0, 'Aucune commune dans le périmètre'
    assert df['insee'].str.fullmatch(r'\w{5}').all(), 'Un code INSEE ne fait pas 5 caractères'
    assert df['insee'].is_unique, 'Commune en double dans le périmètre'
    assert df['nom'].notna().all(), 'Une commune n\'a pas de nom dans perimetre.yml'
