"""Téléchargement HTTP partagé par tous les blocs d'ingestion."""
import time

import requests

# On s'identifie poliment auprès des serveurs publics
USER_AGENT = 'HOMEPEDIA/0.1 (projet ecole, ingestion open data)'


def telecharger(url: str, tentatives: int = 3, pause_s: float = 2.0, timeout_s: int = 120) -> requests.Response:
    """GET avec plusieurs essais. Renvoie la réponse (r.url = URL finale après redirection)."""
    for essai in range(1, tentatives + 1):
        try:
            r = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=timeout_s)
            r.raise_for_status()  # lève une erreur si code HTTP 4xx / 5xx
            return r
        except requests.RequestException as err:
            # Erreur définitive (404 introuvable, 403 interdit...) : réessayer ne sert à rien.
            # On ne réessaie que les erreurs passagères : 5xx, 429 (trop de requêtes), réseau.
            statut = err.response.status_code if err.response is not None else None
            definitive = statut is not None and 400 <= statut < 500 and statut != 429
            if definitive or essai == tentatives:
                raise
            # Attente croissante entre les essais : 2 s, 4 s, 6 s...
            print(f'Essai {essai}/{tentatives} échoué ({err}), nouvel essai dans {pause_s * essai:.0f} s')
            time.sleep(pause_s * essai)
