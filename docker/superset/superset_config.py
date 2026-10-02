"""Configuration Superset HOMEPEDIA (surcharge les valeurs par défaut de superset/config.py)."""
import copy
import os
import sys

# Clé qui chiffre les mots de passe des bases enregistrées dans Superset (lue dans .env)
SECRET_KEY = os.environ['SUPERSET_SECRET_KEY']

# Base INTERNE de Superset (graphiques, dashboards, utilisateurs) : un fichier SQLite,
# rangé dans le volume Docker superset_home. Suffisant pour un prototype.
SQLALCHEMY_DATABASE_URI = 'sqlite:////app/superset_home/superset.db?check_same_thread=false'

# Nombre maximal de lignes renvoyées à un graphique (défaut : 50 000).
# La carte doit pouvoir afficher les ~81 000 parcelles du périmètre.
ROW_LIMIT = 100_000
SQL_MAX_ROW = 100_000

# Politique de sécurité du navigateur (CSP) : liste des adresses d'où une page Superset peut
# charger des images. On reprend celle de Superset (déjà chargée : ce fichier est lu à la fin de
# superset/config.py) et on y ajoute notre stockage S3, pour afficher les photos des cavités.
TALISMAN_CONFIG = copy.deepcopy(sys.modules['superset.config'].TALISMAN_CONFIG)
TALISMAN_CONFIG['content_security_policy']['img-src'].append(
    os.environ.get('S3_URL_PUBLIQUE', 'http://localhost:8333'))

# Fond de carte : rien à configurer. Par défaut, Superset 6 propose des tuiles OpenStreetMap
# (gratuites, sans clé), en plus de Mapbox (qui demanderait une clé MAPBOX_API_KEY).
