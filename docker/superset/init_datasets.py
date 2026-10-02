"""Déclare les tables gold comme "datasets" Superset (ou rafraîchit leurs colonnes si elles existent).

Exécuté par bootstrap.sh à chaque démarrage : si dbt a ajouté une colonne, Superset la découvre.
"""
from superset.app import create_app

TABLES_GOLD = ['parcelles_exposition_cavites', 'communes_synthese', 'carte_elements',
               'galerie_cavites', 'cavites_mots_cles']

app = create_app()
with app.app_context():
    # Imports après create_app : ils ont besoin de l'application initialisée
    from superset import db, security_manager
    from superset.connectors.sqla.models import SqlaTable
    from superset.models.core import Database

    base = db.session.query(Database).filter_by(database_name='homepedia').one()
    admin = security_manager.find_user(username='admin')

    for table in TABLES_GOLD:
        dataset = (db.session.query(SqlaTable)
                   .filter_by(database_id=base.id, schema='gold', table_name=table)
                   .one_or_none())
        if dataset is None:
            dataset = SqlaTable(table_name=table, schema='gold', database=base, owners=[admin])
            db.session.add(dataset)
        try:
            # Lit la liste des colonnes et leurs types directement dans Postgres
            dataset.fetch_metadata()
            print(f'  dataset gold.{table} : {len(dataset.columns)} colonnes')
        except Exception as erreur:
            # Ex. premier lancement de la stack : dbt n'a pas encore créé la table
            print(f'  ATTENTION gold.{table} introuvable ({erreur}) — relancer après dbt')
            db.session.rollback()
            continue
        db.session.commit()
