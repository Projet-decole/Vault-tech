#!/bin/bash
# Enregistre dans le projet les dashboards tels qu'ils sont dans Superset (après modification dans l'interface).
# Usage, depuis la racine du projet :   ./docker/superset/exporter_dashboard.sh
# Puis reconstruire l'image pour que le nouveau dossier soit embarqué :   docker compose build superset
set -e
cd "$(dirname "$0")/../.."

tmp=$(mktemp -d)
docker compose exec -T superset superset export-dashboards -f /tmp/homepedia_export.zip
docker compose cp superset:/tmp/homepedia_export.zip "$tmp/export.zip"
unzip -q "$tmp/export.zip" -d "$tmp"

rm -rf docker/superset/dashboard
mv "$tmp"/dashboard_export_* docker/superset/dashboard
rm -rf "$tmp"

# Le mot de passe est masqué à l'export : on remet des variables, remplacées au démarrage par le .env
sed -i 's|^sqlalchemy_uri: .*|# Variables remplacées au démarrage par importer_dashboard.py (valeurs du .env)\nsqlalchemy_uri: postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}|' \
    docker/superset/dashboard/databases/*.yaml

echo "Dashboards exportés dans docker/superset/dashboard/ — pensez à : docker compose build superset"
