# Image Superset officielle ("lean") + pilote PostgreSQL + nos scripts de démarrage.
FROM apache/superset:6.1.0

USER root
# psycopg2 = pilote Python pour PostgreSQL, absent de l'image allégée.
# Installé dans l'environnement Python de Superset (/app/.venv) avec uv, l'installeur fourni par l'image.
RUN uv pip install --python /app/.venv/bin/python --no-cache psycopg2-binary==2.9.13

# Copiés dans l'image (et non montés depuis l'hôte) : pas de risque de fichier périmé avec Docker Desktop.
# /app/pythonpath est dans le PYTHONPATH de l'image : Superset y charge automatiquement superset_config.py
COPY superset_config.py /app/pythonpath/superset_config.py
COPY bootstrap.sh init_datasets.py importer_dashboard.py /app/homepedia/
# Le dashboard HOMEPEDIA au format d'export Superset (importé au 1er démarrage)
COPY dashboard /app/homepedia/dashboard
# a+rX : lisible par tous (les fichiers exportés par Superset sont en 600, illisibles pour
# l'utilisateur "superset") ; X = droit de traverser les dossiers. bootstrap.sh exécutable.
RUN chmod -R a+rX /app/homepedia && chmod +x /app/homepedia/bootstrap.sh

USER superset
