"""Crée le dashboard « Carte des cavités » : la carte multi-échelle (page MapLibre du conteneur
"carte", tuiles servies par Martin) intégrée dans une iframe, au sein d'un bloc Markdown.

Pourquoi une iframe : Superset ne sait pas changer de couche selon le zoom (régions → départements
→ communes). La carte vit donc dans sa propre page, et Superset l'affiche dans un cadre.
Il faut que superset_config.py autorise l'iframe (CSP frame-src et désinfection du HTML).

Usage (depuis la racine du projet, Superset et le conteneur carte lancés) :
    python3 docker/superset/carte/creer_dashboard_carte.py
Relançable : supprime puis recrée le dashboard.
"""
import json
import pathlib
import sys

# On réutilise le client de l'API Superset (connexion, appels) du test d'échelle
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'test_echelle'))
from creer_test_echelle import URL, Client  # noqa: E402

TITRE = 'Carte des cavités'
SLUG = 'carte-cavites'
CARTE_URL = 'http://localhost:8090'

# Le bloc Markdown accepte du HTML : l'iframe occupe toute sa hauteur
IFRAME = (f'<iframe src="{CARTE_URL}" title="Carte multi-échelle des cavités" loading="lazy" '
          'style="width:100%;height:100%;min-height:720px;border:0"></iframe>')


def main():
    api = Client()
    for i in api.chercher('dashboard', 'slug', SLUG):
        api.appel('DELETE', f'/api/v1/dashboard/{i}')

    # Hauteur en unités de grille de Superset (8 px chacune) : 96 × 8 = 768 px
    position = {
        'DASHBOARD_VERSION_KEY': 'v2',
        'ROOT_ID': {'type': 'ROOT', 'id': 'ROOT_ID', 'children': ['GRID_ID']},
        'GRID_ID': {'type': 'GRID', 'id': 'GRID_ID', 'children': ['ROW-carte'], 'parents': ['ROOT_ID']},
        'ROW-carte': {'type': 'ROW', 'id': 'ROW-carte', 'children': ['MARKDOWN-carte'],
                      'parents': ['ROOT_ID', 'GRID_ID'], 'meta': {'background': 'BACKGROUND_TRANSPARENT'}},
        'MARKDOWN-carte': {'type': 'MARKDOWN', 'id': 'MARKDOWN-carte', 'children': [],
                           'parents': ['ROOT_ID', 'GRID_ID', 'ROW-carte'],
                           'meta': {'width': 12, 'height': 96, 'code': IFRAME}},
    }
    tableau = api.appel('POST', '/api/v1/dashboard/', {
        'dashboard_title': TITRE, 'slug': SLUG, 'published': True,
        'position_json': json.dumps(position)})['id']
    print(f'Dashboard {tableau} : {URL}/superset/dashboard/{SLUG}/')


if __name__ == '__main__':
    main()
