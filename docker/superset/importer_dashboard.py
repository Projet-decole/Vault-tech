"""Importe le dashboard HOMEPEDIA (dossier dashboard/, format d'export Superset) s'il n'existe pas encore.

- Nouvelle installation : base, datasets, graphiques et dashboard sont créés.
- Installation existante : rien n'est touché (on ne veut pas écraser des modifications faites
  dans l'interface). Pour forcer : SUPERSET_FORCE_IMPORT=1 docker compose up -d superset
Les ${VARIABLES} des fichiers YAML (identifiants Postgres) sont remplacées par celles du .env.
"""
import os
from pathlib import Path

import yaml
from superset.app import create_app

DOSSIER = Path('/app/homepedia/dashboard')

app = create_app()
with app.app_context():
    # Imports après create_app : ils ont besoin de l'application initialisée
    from superset import security_manager
    from superset.commands.dashboard.importers.dispatcher import ImportDashboardsCommand
    from superset.extensions import db
    from superset.models.dashboard import Dashboard
    from superset.utils.core import override_user

    uuids = [yaml.safe_load(f.read_text())['uuid'] for f in (DOSSIER / 'dashboards').glob('*.yaml')]
    deja_la = db.session.query(Dashboard).filter(Dashboard.uuid.in_(uuids)).count() == len(uuids)
    if deja_la and os.environ.get('SUPERSET_FORCE_IMPORT') != '1':
        print('  dashboard déjà présent : import ignoré (SUPERSET_FORCE_IMPORT=1 pour écraser)')
    else:
        # {chemin relatif: contenu YAML}, avec les ${VARIABLES} remplacées
        contenus = {str(f.relative_to(DOSSIER)): os.path.expandvars(f.read_text())
                    for f in DOSSIER.rglob('*.yaml')}
        with override_user(security_manager.find_user(username='admin')):
            ImportDashboardsCommand(contenus, overwrite=True).run()
        print(f'  dashboard importé ({len(contenus)} fichiers)')
