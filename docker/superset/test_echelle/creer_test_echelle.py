"""Test d'échelle de Superset : crée un dashboard « Test échelle nationale » avec trois cartes
choroplèthes (régions, départements, communes de France), coloriées selon la densité de cavités.

Usage (depuis la racine du projet, Superset lancé) :
    python3 docker/superset/test_echelle/creer_test_echelle.py
Le mot de passe admin est lu dans .env (SUPERSET_ADMIN_PASSWORD). Relançable : supprime puis recrée.

Pourquoi des couleurs calculées en SQL : le graphique deck.gl GeoJSON de Superset accepte des
contours complets (MultiPolygon : les îles, la Corse...) mais ne colorie pas selon une mesure ;
le graphique deck.gl Polygon colorie, mais ne lit qu'un anneau de coordonnées (pas de MultiPolygon).
On classe donc chaque territoire en SQL (0 = aucune cavité, puis 6 classes d'effectifs égaux) et on
écrit sa couleur dans le GeoJSON, comme le fait déjà la carte des parcelles.
"""
import json
import pathlib
import urllib.request
from http.cookiejar import CookieJar

RACINE = pathlib.Path(__file__).resolve().parents[3]
URL = 'http://localhost:8088'
TITRE = 'Test échelle nationale'
# Palette séquentielle jaune → rouge (ColorBrewer YlOrRd), classe 0 en gris clair
COULEURS = ['#f0f0f0', '#ffffb2', '#fed976', '#feb24c', '#fd8d3c', '#f03b20', '#bd0026']

NIVEAUX = [
    # (table gold, colonne code, colonne nom, couleur des bordures, titre)
    ('cavites_par_region', 'code_region', 'nom_region', '#555555', 'Régions'),
    ('cavites_par_departement', 'code_departement', 'nom_departement', '#777777', 'Départements'),
    ('cavites_par_commune', 'code_insee', 'nom_commune', '#00000000', 'Communes (35 000)'),
    # Même carte, contours simplifiés par PostGIS (tolérance 0,005° ≈ 500 m) : combien gagne-t-on ?
    ('cavites_par_commune', 'code_insee', 'nom_commune', '#00000000', 'Communes simplifiées'),
]


def sql_choroplethe(table: str, code: str, nom: str, bordure: str, titre: str = '') -> str:
    palette = ','.join(f"'{c}'" for c in COULEURS)
    # public. : les fonctions PostGIS vivent dans le schéma public, que Superset ne cherche pas
    # quand le dataset est rattaché au schéma gold
    geometrie = ("public.ST_AsGeoJSON(public.ST_SimplifyPreserveTopology("
                 "public.ST_GeomFromGeoJSON(geometrie_geojson), 0.005), 4)::json"
                 if 'simplifiées' in titre else 'geometrie_geojson::json')
    return f"""
with classes as (
    select *,
           case when nb_cavites = 0 then 0
                else ntile(6) over (partition by nb_cavites > 0 order by cavites_pour_100_km2) end as classe
    from gold.{table}
)
select {code} as code, {nom} as nom, nb_cavites, cavites_pour_100_km2, classe,
       json_build_object(
           'type', 'Feature',
           'geometry', {geometrie},
           'properties', json_build_object(
               'fillColor', (array[{palette}])[classe + 1],
               'strokeColor', '{bordure}',
               'libelle', {nom} || ' : ' || nb_cavites || ' cavités, ' || cavites_pour_100_km2 || ' pour 100 km²'
           )
       )::text as geojson
from classes
where geometrie_geojson is not null
"""


class Client:
    def __init__(self):
        self.ouvreur = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
        env = dict(l.split('=', 1) for l in (RACINE / '.env').read_text().splitlines()
                   if '=' in l and not l.lstrip().startswith('#'))
        jeton = self.appel('POST', '/api/v1/security/login', {
            'username': 'admin', 'password': env['SUPERSET_ADMIN_PASSWORD'].strip(),
            'provider': 'db', 'refresh': False})['access_token']
        self.entetes = {'Authorization': f'Bearer {jeton}'}
        self.entetes['X-CSRFToken'] = self.appel('GET', '/api/v1/security/csrf_token/')['result']

    def appel(self, methode: str, chemin: str, corps=None):
        requete = urllib.request.Request(
            URL + chemin, method=methode,
            data=json.dumps(corps).encode() if corps is not None else None,
            headers={'Content-Type': 'application/json', 'Referer': URL, **getattr(self, 'entetes', {})})
        with self.ouvreur.open(requete) as r:
            texte = r.read()
        return json.loads(texte) if texte else {}

    def chercher(self, ressource: str, colonne: str, valeur: str, operateur: str = 'eq') -> list:
        q = urllib.request.quote(json.dumps(
            {'filters': [{'col': colonne, 'opr': operateur, 'value': valeur}], 'page_size': 100}))
        return [r['id'] for r in self.appel('GET', f'/api/v1/{ressource}/?q={q}')['result']]


def main():
    api = Client()
    base = api.chercher('database', 'database_name', 'homepedia')[0]

    # Relançable : on supprime d'abord ce qu'une exécution précédente a créé
    for i in api.chercher('dashboard', 'slug', 'test-echelle'):
        api.appel('DELETE', f'/api/v1/dashboard/{i}')
    for i in api.chercher('chart', 'slice_name', 'Test échelle', 'sw'):
        api.appel('DELETE', f'/api/v1/chart/{i}')
    for i in api.chercher('dataset', 'table_name', 'test_echelle_', 'sw'):
        api.appel('DELETE', f'/api/v1/dataset/{i}')
    graphiques = []
    for table, code, nom, bordure, titre in NIVEAUX:
        nom_dataset = f'test_echelle_{table}' + ('_simplifie' if 'simplifiées' in titre else '')

        dataset = api.appel('POST', '/api/v1/dataset/', {
            'database': base, 'schema': 'gold', 'table_name': nom_dataset,
            'sql': sql_choroplethe(table, code, nom, bordure, titre)})['id']
        params = {
            'datasource': f'{dataset}__table', 'viz_type': 'deck_geojson', 'geojson': 'geojson',
            'row_limit': 100000, 'filter_nulls': True, 'adhoc_filters': [],
            'mapbox_style': 'https://tile.openstreetmap.org/{z}/{x}/{y}.png', 'autozoom': False,
            'viewport': {'longitude': 2.5, 'latitude': 46.6, 'zoom': 4.6, 'bearing': 0, 'pitch': 0},
            'filled': True, 'stroked': True, 'extruded': False,
            'fill_color_picker': {'r': 0, 'g': 0, 'b': 0, 'a': 0},
            'stroke_color_picker': {'r': 0, 'g': 0, 'b': 0, 'a': 0},
            'line_width': 1, 'line_width_unit': 'pixels', 'point_radius_scale': 25,
        }
        graphique = api.appel('POST', '/api/v1/chart/', {
            'slice_name': f'Test échelle · {titre}', 'viz_type': 'deck_geojson',
            'datasource_id': dataset, 'datasource_type': 'table', 'params': json.dumps(params)})['id']
        graphiques.append(graphique)
        print(f'{titre} : dataset {dataset}, graphique {graphique}')

    # Mise en page : les trois cartes côte à côte
    ligne = {'type': 'ROW', 'id': 'ROW-cartes', 'children': [f'CHART-{g}' for g in graphiques],
             'parents': ['ROOT_ID', 'GRID_ID'], 'meta': {'background': 'BACKGROUND_TRANSPARENT'}}
    position = {'DASHBOARD_VERSION_KEY': 'v2',
                'ROOT_ID': {'type': 'ROOT', 'id': 'ROOT_ID', 'children': ['GRID_ID']},
                'GRID_ID': {'type': 'GRID', 'id': 'GRID_ID', 'children': ['ROW-cartes'], 'parents': ['ROOT_ID']},
                'ROW-cartes': ligne}
    for g in graphiques:
        position[f'CHART-{g}'] = {'type': 'CHART', 'id': f'CHART-{g}', 'children': [],
                                  'parents': ['ROOT_ID', 'GRID_ID', 'ROW-cartes'],
                                  'meta': {'chartId': g, 'width': 12 // len(graphiques), 'height': 80}}
    tableau = api.appel('POST', '/api/v1/dashboard/', {
        'dashboard_title': TITRE, 'slug': 'test-echelle', 'published': False,
        'position_json': json.dumps(position)})['id']
    for g in graphiques:  # rattacher chaque graphique au dashboard
        api.appel('PUT', f'/api/v1/chart/{g}', {'dashboards': [tableau]})
    print(f'Dashboard : {URL}/superset/dashboard/test-echelle/')


if __name__ == '__main__':
    main()
