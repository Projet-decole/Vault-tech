#!/bin/bash
# Démarrage de Superset. Chaque étape est sans danger si on la rejoue (conteneur redémarré).
set -e

echo '1/6 Création / mise à jour de la base interne de Superset'
superset db upgrade

echo '2/6 Compte administrateur (ignoré s il existe déjà)'
superset fab create-admin \
    --username admin --firstname Admin --lastname HOMEPEDIA \
    --email admin@homepedia.local --password "$SUPERSET_ADMIN_PASSWORD" || true

echo '3/6 Rôles et permissions par défaut'
superset init

echo '4/6 Dashboard HOMEPEDIA (base, datasets, graphiques) depuis docker/superset/dashboard/'
python /app/homepedia/importer_dashboard.py

echo '5/6 Connexion à la base homepedia (mot de passe du .env)'
superset set-database-uri --database_name homepedia \
    --uri "postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}"

echo '6/6 Datasets sur les tables gold (colonnes rafraîchies)'
python /app/homepedia/init_datasets.py

echo 'Démarrage du serveur web sur le port 8088'
exec /usr/bin/run-server.sh
