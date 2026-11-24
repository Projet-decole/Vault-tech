"""Mesure côté serveur des cartes du test d'échelle : temps de réponse de Superset et poids des données
envoyées au navigateur, pour chaque graphique « Test échelle · ... ». Trois essais : le premier
interroge PostgreSQL, les suivants peuvent venir du cache de Superset.

Usage : python3 docker/superset/test_echelle/mesurer_test_echelle.py
"""
import json
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from creer_test_echelle import URL, Client  # noqa: E402


def connexion_navigateur(api: Client) -> None:
    """Les cartes deck.gl passent par l'ancien point d'accès explore_json, qui exige une session
    (cookie) comme un navigateur : on remplit le formulaire de connexion."""
    import pathlib
    import re
    page = api.ouvreur.open(f'{URL}/login/').read().decode()
    csrf = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', page).group(1)
    env = dict(l.split('=', 1) for l in (pathlib.Path(__file__).resolve().parents[3] / '.env').read_text().splitlines()
               if '=' in l and not l.lstrip().startswith('#'))
    corps = urllib.parse.urlencode({'csrf_token': csrf, 'username': 'admin',
                                    'password': env['SUPERSET_ADMIN_PASSWORD'].strip()}).encode()
    api.ouvreur.open(urllib.request.Request(f'{URL}/login/', data=corps, method='POST',
                                            headers={'Referer': f'{URL}/login/'}))
    api.entetes = {'X-CSRFToken': csrf}


def main():
    api = Client()
    connexion_navigateur(api)
    q = urllib.parse.quote(json.dumps({'filters': [{'col': 'slice_name', 'opr': 'sw', 'value': 'Test échelle'}]}))
    graphiques = api.appel('GET', f'/api/v1/chart/?q={q}')['result']
    for g in sorted(graphiques, key=lambda g: g['id']):
        mesures = []
        for essai in range(3):
            corps = urllib.parse.urlencode({'form_data': json.dumps({'slice_id': g['id']})}).encode()
            requete = urllib.request.Request(
                f"{URL}/superset/explore_json/?force={'true' if essai == 0 else 'false'}",
                data=corps, method='POST',
                headers={'Content-Type': 'application/x-www-form-urlencoded', 'Referer': URL, **api.entetes})
            debut = time.perf_counter()
            with api.ouvreur.open(requete) as r:
                brut = r.read()
            duree = time.perf_counter() - debut
            reponse = json.loads(brut)
            nb = len((reponse.get('data') or {}).get('features', []))
            mesures.append((duree, len(brut), nb))
        d0, taille, nb = mesures[0]
        print(f"{g['slice_name']:<35} {nb:>6} territoires · {taille / 1e6:6.1f} Mo · "
              f"1re requête {d0:5.2f} s · suivantes {mesures[1][0]:5.2f} s / {mesures[2][0]:5.2f} s")


if __name__ == '__main__':
    main()
