"""Bloc — Index MongoDB + recherche plein texte dans les fiches cavités.

1. Index texte (français) sur le nom et les commentaires, index géographique sur le point GPS.
2. Démonstration géographique : cavités à moins de 1 km du Hackenberg (dans les logs).
3. Nombre de fiches mentionnant chaque mot-clé métier, par département.
4. Écrit ce comptage dans silver.cavites_mots_cles : Superset ne sait pas lire MongoDB,
   on lui prépare donc le résultat dans Postgres.
"""
from homepedia.utils.bases import base_mongo, connexion_postgres

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom

# Mots utiles à un constructeur de bunkers. Grâce à l'index "french", un mot trouve aussi
# ses variantes (effondrement → effondré, effondrements ; galerie → galeries...).
MOTS_CLES = [
    'effondrement', 'affaissement', 'galerie', 'puits', 'eau', 'inondé',
    'gypse', 'calcaire', 'blockhaus', 'casemate', 'remblai', 'entrée',
]


@custom
def mongo_index_et_mots_cles(*args, **kwargs) -> None:
    fiches = base_mongo()['cavites_fiches']

    # --- 1. Index (sans effet s'ils existent déjà ; recréés si Spark a vidé la collection) ---
    fiches.create_index([('identification.nom', 'text'), ('description.commentaires', 'text')],
                        default_language='french', name='recherche_texte')
    fiches.create_index([('localisation.point', '2dsphere')], name='position')

    # --- 2. Démonstration géographique : $near trie les fiches par distance à un point ---
    hackenberg = fiches.find_one({'_id': 'LORAW0005855'}, {'localisation.point': 1})
    if hackenberg:
        proches = fiches.find(
            {'localisation.point': {'$near': {'$geometry': hackenberg['localisation']['point'],
                                              '$maxDistance': 1000}}},   # en mètres
            {'identification.nom': 1, 'identification.type': 1},
        )
        print('Cavités à moins de 1 km du Hackenberg :')
        for f in proches:
            print(f"  {f['_id']}  {f['identification']['type']:18s}  {f['identification'].get('nom')}")

    # --- 3. Comptage des mots-clés par département ($text utilise l'index texte) ---
    lignes = []
    for mot in MOTS_CLES:
        resultats = fiches.aggregate([
            {'$match': {'$text': {'$search': mot}}},
            {'$group': {'_id': '$localisation.departement', 'nb_fiches': {'$sum': 1}}},
        ])
        for r in resultats:
            lignes.append((mot, r['_id'], r['nb_fiches']))
    print(f'{len(MOTS_CLES)} mots-clés recherchés, {len(lignes)} couples (mot, département) trouvés')

    # --- 4. Résultat vers Postgres ---
    connexion = connexion_postgres()
    with connexion, connexion.cursor() as curseur:
        curseur.execute("""
            create table if not exists silver.cavites_mots_cles (
                mot_cle     text not null,
                departement text not null,
                nb_fiches   integer not null,
                primary key (mot_cle, departement)
            )
        """)
        curseur.execute('truncate silver.cavites_mots_cles')   # truncate : les vues dbt restent valides
        curseur.executemany('insert into silver.cavites_mots_cles values (%s, %s, %s)', lignes)
    connexion.close()
