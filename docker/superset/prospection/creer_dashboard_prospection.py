"""Crée le dashboard « Prospection » : le parcours d'un prospecteur (entreprise qui construit ou
réhabilite des bunkers), de la France à la commune.

Les mêmes cavités se lisent de deux façons :
  - opportunité : les ouvrages militaires, des existants à réhabiliter ;
  - risque : les cavités naturelles et les carrières, qui menacent un projet neuf (effondrement).

Onglet « France » : chiffres clés, carte multi-échelle (iframe vers le conteneur "carte"), puis un
tableau triable, filtrable et exportable (CSV) par niveau : régions, départements, communes.
Filtres : Région, puis Département (en cascade). La carte, dans son iframe, ne suit pas les filtres.
Onglet « Commune » : les graphiques et le filtre Commune du dashboard « Cavités & parcelles »,
repris tels quels (ce dashboard doit exister : il est importé au premier démarrage de Superset).

Usage (depuis la racine du projet, Superset et le conteneur carte lancés, tables gold à jour) :
    python3 docker/superset/prospection/creer_dashboard_prospection.py
Relançable : supprime puis recrée le dashboard et ses graphiques.
"""
import json
import pathlib
import sys

# On réutilise le client de l'API Superset (connexion, appels) du test d'échelle
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'test_echelle'))
from creer_test_echelle import URL, Client  # noqa: E402

TITRE = 'Prospection : cavités de France'
SLUG = 'prospection'
PREFIXE = 'Prospection · '   # nom des graphiques créés ici (pour les retrouver et les supprimer)
# Même adresse que Superset vu par nginx (port 8090) : la carte peut alors lire et modifier les filtres
CARTE_URL = 'http://localhost:8090/carte/'
COUVERTURE = 'Parcelles analysées : Rhône, Loire et 6 communes de Moselle'

# Libellés lisibles des colonnes (verbose_name des datasets), partagés par les trois niveaux
LIBELLES = {
    'nom_region': 'Région', 'nom_departement': 'Département', 'nom_commune': 'Commune',
    'code_region': 'Code région', 'code_departement': 'Code dép.', 'code_insee': 'Code INSEE',
    'nb_communes': 'Communes', 'nb_communes_avec_cavite': 'Communes avec cavité',
    'pct_communes_avec_cavite': '% communes avec cavité',
    'nb_cavites': 'Cavités', 'cavites_pour_100_km2': 'Cavités / 100 km²',
    'nb_ouvrages_militaires': 'Ouvrages militaires', 'nb_cavites_naturelles': 'Cavités naturelles',
    'nb_carrieres': 'Carrières', 'nb_caves': 'Caves', 'nb_ouvrages_civils': 'Ouvrages civils',
    'nb_indeterminees': 'Indéterminées', 'superficie_km2': 'Superficie (km²)',
    'nb_communes_analysees': 'Communes analysées', 'nb_parcelles_analysees': 'Parcelles analysées',
    'nb_parcelles_exposition_forte': 'Parcelles à < 200 m', 'nb_parcelles_proximite': 'Parcelles à 200-500 m',
    'pct_parcelles_exposees': '% parcelles à < 500 m',
}

FAMILLES = ['nb_ouvrages_militaires', 'nb_cavites_naturelles', 'nb_carrieres', 'nb_caves', 'nb_ouvrages_civils']
PARCELLES = ['nb_parcelles_analysees', 'pct_parcelles_exposees']

# (table gold, titre de l'onglet, colonnes du tableau)
NIVEAUX = [
    ('cavites_par_region', 'Régions',
     ['nom_region', 'nb_cavites', 'cavites_pour_100_km2', *FAMILLES, 'pct_communes_avec_cavite', *PARCELLES]),
    ('cavites_par_departement', 'Départements',
     ['nom_departement', 'nom_region', 'nb_cavites', 'cavites_pour_100_km2', *FAMILLES,
      'pct_communes_avec_cavite', *PARCELLES]),
    ('cavites_par_commune', 'Communes',
     ['nom_commune', 'nom_departement', 'nom_region', 'nb_cavites', 'cavites_pour_100_km2', *FAMILLES,
      'nb_parcelles_analysees', 'nb_parcelles_exposition_forte', 'pct_parcelles_exposees']),
]

# Chiffres clés, calculés sur les communes (pour suivre les filtres Région et Département)
CHIFFRES = [
    ('Cavités recensées', 'SUM(nb_cavites)', 'BRGM, toute la France'),
    ('Ouvrages militaires', 'SUM(nb_ouvrages_militaires)', 'Opportunités : existants à réhabiliter'),
    ('Cavités naturelles et carrières', 'SUM(nb_cavites_naturelles + nb_carrieres)',
     "Risques : effondrement sous un projet neuf"),
    ('Parcelles à moins de 500 m', 'SUM(nb_parcelles_exposition_forte + nb_parcelles_proximite)', COUVERTURE),
]


def libeller_dataset(api: Client, dataset: int) -> None:
    """Rafraîchit les colonnes du dataset (dbt a pu en ajouter) et pose les libellés lisibles."""
    api.appel('PUT', f'/api/v1/dataset/{dataset}/refresh')
    colonnes = api.appel('GET', f'/api/v1/dataset/{dataset}')['result']['columns']
    autorisees = {'id', 'column_name', 'type', 'verbose_name', 'description', 'expression', 'filterable',
                  'groupby', 'is_active', 'is_dttm', 'python_date_format', 'advanced_data_type', 'extra', 'uuid'}
    nouvelles = []
    for c in colonnes:
        c = {k: v for k, v in c.items() if k in autorisees and v is not None}
        if c['column_name'] in LIBELLES:
            c['verbose_name'] = LIBELLES[c['column_name']]
        nouvelles.append(c)
    api.appel('PUT', f'/api/v1/dataset/{dataset}', {'columns': nouvelles})


def creer_graphique(api: Client, nom: str, viz: str, dataset: int, params: dict) -> int:
    params = {'datasource': f'{dataset}__table', 'viz_type': viz, 'adhoc_filters': [], **params}
    return api.appel('POST', '/api/v1/chart/', {
        'slice_name': PREFIXE + nom, 'viz_type': viz, 'datasource_id': dataset,
        'datasource_type': 'table', 'params': json.dumps(params)})['id']


def main():
    api = Client()

    # Relançable : on supprime ce qu'une exécution précédente a créé
    # (et l'ancien dashboard « Carte des cavités », que celui-ci remplace)
    for slug in (SLUG, 'carte-cavites'):
        for i in api.chercher('dashboard', 'slug', slug):
            api.appel('DELETE', f'/api/v1/dashboard/{i}')
    for i in api.chercher('chart', 'slice_name', PREFIXE, 'sw'):
        api.appel('DELETE', f'/api/v1/chart/{i}')

    datasets = {}
    for table, _, _ in NIVEAUX:
        datasets[table] = api.chercher('dataset', 'table_name', table)[0]
        libeller_dataset(api, datasets[table])
    communes = datasets['cavites_par_commune']

    # --- Chiffres clés ---
    chiffres = []
    for titre, sql, sous_titre in CHIFFRES:
        chiffres.append(creer_graphique(api, titre, 'big_number_total', communes, {
            'metric': {'expressionType': 'SQL', 'sqlExpression': sql, 'label': titre},
            'subheader': sous_titre, 'y_axis_format': ',d', 'header_font_size': 0.4,
            'subheader_font_size': 0.15}))

    # --- Un tableau par niveau : tri au clic sur l'en-tête, recherche, export CSV (menu du graphique) ---
    tableaux = {}
    for table, titre, colonnes in NIVEAUX:
        tableaux[table] = creer_graphique(api, f'Tableau {titre.lower()}', 'table', datasets[table], {
            'query_mode': 'raw', 'all_columns': colonnes,
            'order_by_cols': [json.dumps(['nb_cavites', False])],
            'server_pagination': True, 'server_page_length': 50, 'row_limit': 50000,
            'include_search': True, 'show_cell_bars': True, 'allow_rearrange_columns': True,
            'table_timestamp_format': 'smart_date'})

    # --- Mise en page ---
    position = {'DASHBOARD_VERSION_KEY': 'v2',
                'ROOT_ID': {'type': 'ROOT', 'id': 'ROOT_ID', 'children': ['TABS-principal']}}

    def ajouter(id_, type_, parents, enfants=(), meta=None):
        position[id_] = {'type': type_, 'id': id_, 'children': list(enfants), 'parents': parents,
                         'meta': meta or {}}

    ajouter('TABS-principal', 'TABS', ['ROOT_ID'], ['TAB-france', 'TAB-commune'])
    p_france = ['ROOT_ID', 'TABS-principal', 'TAB-france']
    ajouter('TAB-france', 'TAB', p_france[:2], ['ROW-chiffres', 'ROW-carte', 'TABS-niveaux'],
            {'text': 'France', 'defaultText': 'Onglet'})

    ajouter('ROW-chiffres', 'ROW', p_france, [f'CHART-{c}' for c in chiffres],
            {'background': 'BACKGROUND_TRANSPARENT'})
    for c in chiffres:
        ajouter(f'CHART-{c}', 'CHART', p_france + ['ROW-chiffres'], meta={'chartId': c, 'width': 3, 'height': 28})

    iframe = (f'<iframe src="{CARTE_URL}" title="Carte multi-échelle des cavités" loading="lazy" '
              'style="width:100%;height:100%;min-height:640px;border:0"></iframe>')
    ajouter('ROW-carte', 'ROW', p_france, ['MARKDOWN-carte'], {'background': 'BACKGROUND_TRANSPARENT'})
    ajouter('MARKDOWN-carte', 'MARKDOWN', p_france + ['ROW-carte'],
            meta={'width': 12, 'height': 84, 'code': iframe})

    onglets = [f'TAB-{t}' for t, _, _ in NIVEAUX]
    ajouter('TABS-niveaux', 'TABS', p_france, onglets)
    for table, titre, _ in NIVEAUX:
        p = p_france + ['TABS-niveaux', f'TAB-{table}']
        ajouter(f'TAB-{table}', 'TAB', p[:-1], [f'ROW-{table}'], {'text': titre, 'defaultText': 'Onglet'})
        ajouter(f'ROW-{table}', 'ROW', p, [f'CHART-{tableaux[table]}'], {'background': 'BACKGROUND_TRANSPARENT'})
        ajouter(f'CHART-{tableaux[table]}', 'CHART', p + [f'ROW-{table}'],
                meta={'chartId': tableaux[table], 'width': 12, 'height': 90})

    # --- Onglet Commune : la mise en page et les graphiques du dashboard « Cavités & parcelles »,
    # repris tels quels (mêmes graphiques, rattachés aux deux dashboards). Les identifiants des blocs
    # reçoivent le suffixe "-commune" pour ne pas entrer en collision avec ceux de l'onglet France.
    ancien = api.appel('GET', '/api/v1/dashboard/cavites-parcelles')['result']
    ancienne_page = json.loads(ancien['position_json'])
    anciens_filtres = json.loads(ancien['json_metadata']).get('native_filter_configuration', [])
    p_commune = ['ROOT_ID', 'TABS-principal', 'TAB-commune']
    lignes = ancienne_page['GRID_ID']['children']
    ajouter('TAB-commune', 'TAB', p_commune[:2], [f'{l}-commune' for l in lignes],
            {'text': 'Commune', 'defaultText': 'Onglet'})
    graphiques_commune = []
    for ligne in lignes:
        bloc = ancienne_page[ligne]
        ajouter(f'{ligne}-commune', 'ROW', p_commune, [f'{e}-commune' for e in bloc['children']], bloc.get('meta'))
        for enfant in bloc['children']:
            e = ancienne_page[enfant]
            ajouter(f'{enfant}-commune', e['type'], p_commune + [f'{ligne}-commune'], meta=e['meta'])
            if e['type'] == 'CHART':
                graphiques_commune.append(e['meta']['chartId'])

    # --- Filtres. Région, puis Département (ses choix se limitent à la région choisie) : onglet France.
    # Commune (obligatoire, repris de l'ancien dashboard) : onglet Commune.
    def filtre(id_, nom, colonne, onglet, parents=(), exclus=()):
        return {'id': id_, 'name': nom, 'filterType': 'filter_select', 'type': 'NATIVE_FILTER',
                'targets': [{'datasetId': communes, 'column': {'name': colonne}}],
                'controlValues': {'multiSelect': True, 'enableEmptyFilter': False, 'inverseSelection': False,
                                  'searchAllOptions': False, 'defaultToFirstItem': False},
                'defaultDataMask': {'extraFormData': {}, 'filterState': {}, 'ownState': {}},
                'cascadeParentIds': list(parents), 'scope': {'rootPath': [onglet], 'excluded': list(exclus)},
                'description': ''}

    filtres = [
        filtre('NATIVE_FILTER-region', 'Région', 'nom_region', 'TAB-france'),
        # le tableau des régions n'a pas de colonne département : hors de portée de ce filtre
        filtre('NATIVE_FILTER-departement', 'Département', 'nom_departement', 'TAB-france',
               parents=['NATIVE_FILTER-region'], exclus=[tableaux['cavites_par_region']]),
    ]
    for f in anciens_filtres:
        f = dict(f, scope=dict(f['scope'], rootPath=['TAB-commune']))
        f.pop('chartsInScope', None)   # recalculé par Superset
        filtres.append(f)
    metadata = {'native_filter_configuration': filtres, 'cross_filters_enabled': False}

    tableau = api.appel('POST', '/api/v1/dashboard/', {
        'dashboard_title': TITRE, 'slug': SLUG, 'published': True,
        'position_json': json.dumps(position), 'json_metadata': json.dumps(metadata)})['id']
    for g in chiffres + list(tableaux.values()):   # rattacher chaque graphique au dashboard
        api.appel('PUT', f'/api/v1/chart/{g}', {'dashboards': [tableau]})
    for g in graphiques_commune:   # les graphiques repris restent aussi dans « Cavités & parcelles »
        api.appel('PUT', f'/api/v1/chart/{g}', {'dashboards': [ancien['id'], tableau]})
    print(f'Dashboard {tableau} : {URL}/superset/dashboard/{SLUG}/')


if __name__ == '__main__':
    main()
