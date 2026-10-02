#!/bin/sh
# Démarrage de SeaweedFS (stockage de fichiers compatible S3) en mode "mini" : tout en un conteneur.
set -e

# Identités S3 (qui a le droit de faire quoi), générées à partir du .env :
#   - homepedia : clé d'accès utilisée par Mage, tous les droits (écrire, lire, lister...)
#   - anonymous : n'importe qui, SANS clé, peut seulement LIRE le bucket "medias"
#                 → le navigateur peut afficher les images dans Superset
cat > /tmp/s3.json <<EOF
{
  "identities": [
    {
      "name": "homepedia",
      "credentials": [{"accessKey": "${S3_ACCESS_KEY}", "secretKey": "${S3_SECRET_KEY}"}],
      "actions": ["Admin", "Read", "List", "Tagging", "Write"]
    },
    {
      "name": "anonymous",
      "actions": ["Read:medias"]
    }
  ]
}
EOF
chmod 644 /tmp/s3.json

# /entrypoint.sh = script de l'image officielle (règle les droits sur /data, puis lance weed)
#   -ip=seaweedfs     nom sous lequel les autres conteneurs joignent ce service
#   -s3.config        identités ci-dessus ; -bucket=medias : créé au démarrage s'il n'existe pas
#   -admin.password   protège l'interface d'administration (utilisateur "admin")
exec /entrypoint.sh mini \
    -ip=seaweedfs \
    -s3.config=/tmp/s3.json \
    -bucket=medias \
    -admin.password="${SEAWEEDFS_ADMIN_PASSWORD}"
