"""Bloc — Règle de rétention du bronze : garde les N dernières ingestions, supprime les plus anciennes.

HDFS garde un dossier ingest_date=<jour> par exécution et par département. Sans règle, le bronze
grossirait indéfiniment (~1 Go de plus par exécution pour le Rhône). On garde les N plus récentes
(par défaut 4 = un mois avec le trigger hebdomadaire) : assez pour comparer ou rejouer un nettoyage.

Exécuté juste après l'ingestion (donc seulement si elle a réussi). Ne supprime jamais la plus récente.
"""
import os

from homepedia.utils.hdfs import client_hdfs

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom

A_GARDER = max(1, int(os.environ.get('RETENTION_BRONZE_INGESTIONS', '4')))


@custom
def retention_bronze(*args, **kwargs) -> None:
    client = client_hdfs()
    libere, supprimes = 0, 0
    for source in client.list('/bronze'):                              # cadastre, cavites
        for dep in client.list(f'/bronze/{source}'):                   # dep=57, dep=69
            dates = sorted(d for d in client.list(f'/bronze/{source}/{dep}') if d.startswith('ingest_date='))
            # Le format AAAA-MM-JJ se trie comme du texte : les N dernières sont les plus récentes
            for ancienne in dates[:-A_GARDER]:
                chemin = f'/bronze/{source}/{dep}/{ancienne}'
                taille = client.content(chemin)['length']              # octets (lu dans le "sommaire")
                client.delete(chemin, recursive=True)
                libere += taille
                supprimes += 1
                print(f'  supprimé : {chemin} ({taille / 1e6:.0f} Mo)')
    print(f'Rétention bronze : {A_GARDER} ingestions gardées par département ; '
          f'{supprimes} dossier(s) supprimé(s), {libere / 1e6:.0f} Mo libérés')
