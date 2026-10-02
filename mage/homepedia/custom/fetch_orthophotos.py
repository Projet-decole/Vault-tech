"""Bloc — Photo aérienne (IGN) de chaque cavité affichée sur la carte, rangée dans le bucket S3 "medias".

Pour chaque cavité de gold.carte_elements (cavités à moins de 500 m d'une parcelle du périmètre) :
  1. demande à l'IGN une photo aérienne de 300 m × 300 m centrée sur la cavité (service WMS gratuit) ;
  2. la range dans le bucket : medias/orthophotos/<code_insee de la cavité>/<id_cavite>.jpg ;
  3. enregistre sa fiche dans silver.medias (la base garde le CHEMIN, pas l'image) ;
  4. ajoute le lien de la photo dans la fiche MongoDB de la cavité.
Incrémental : une cavité qui a DÉJÀ une photo n'est pas re-téléchargée (les photos IGN changent
tous les ~3 ans). On raisonne sur l'identifiant de la cavité, pas sur le chemin du fichier : un chemin
calculé à partir d'une donnée qui bouge créerait des doublons.
"""
import os
import time

import boto3
import requests

from homepedia.utils.bases import base_mongo, connexion_postgres
from homepedia.utils.http import telecharger

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom

BUCKET = 'medias'
DEMI_COTE_M = 150      # photo de 300 m × 300 m
TAILLE_PX = 512        # 512 px pour 300 m ≈ 60 cm par pixel
# Service WMS de la Géoplateforme IGN : photographies aériennes (BD ORTHO), sans clé
WMS = ('https://data.geopf.fr/wms-r?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap'
       '&LAYERS=ORTHOIMAGERY.ORTHOPHOTOS&STYLES=&CRS=EPSG:2154&FORMAT=image/jpeg'
       '&WIDTH={px}&HEIGHT={px}&BBOX={xmin},{ymin},{xmax},{ymax}')
# Adresse du bucket vue depuis le NAVIGATEUR (≠ http://seaweedfs:8333, qui n'existe que dans Docker)
URL_PUBLIQUE = os.environ.get('S3_URL_PUBLIQUE', 'http://localhost:8333')


@custom
def fetch_orthophotos(*args, **kwargs) -> None:
    s3 = boto3.client('s3', endpoint_url='http://seaweedfs:8333', region_name='us-east-1',
                      aws_access_key_id=os.environ['S3_ACCESS_KEY'],
                      aws_secret_access_key=os.environ['S3_SECRET_KEY'])
    connexion = connexion_postgres()
    with connexion, connexion.cursor() as curseur:
        # Crée silver.medias si besoin : même script que l'initialisation de Postgres (une seule définition)
        curseur.execute(open('/sql/init/01_medias.sql', encoding='utf-8').read())
        # Cavités de la carte + emprise de 300 m autour (en Lambert-93, donc en mètres)
        curseur.execute("""
            -- s.code_insee = commune de la cavité elle-même (stable), pas celle de la parcelle la plus proche
            select c.identifiant, s.code_insee,
                   ST_X(s.geom) - %(d)s, ST_Y(s.geom) - %(d)s, ST_X(s.geom) + %(d)s, ST_Y(s.geom) + %(d)s
            from gold.carte_elements c
            join staging.stg_cavites s on s.id_cavite = c.identifiant
            where c.type_element = 'cavite'
        """, {'d': DEMI_COTE_M})
        cavites = curseur.fetchall()
        curseur.execute("select id_objet from silver.medias where type_objet = 'cavite' and type_media = 'orthophoto'")
        deja_la = {ligne[0] for ligne in curseur.fetchall()}   # cavités qui ont déjà leur photo

        nouvelles, echecs = 0, []
        for id_cavite, insee, xmin, ymin, xmax, ymax in cavites:
            if id_cavite in deja_la:
                continue
            cle = f'orthophotos/{insee}/{id_cavite}.jpg'
            url = WMS.format(px=TAILLE_PX, xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)
            try:
                image = telecharger(url).content
            except requests.RequestException as erreur:
                # Une photo manquante ne doit pas faire échouer tout le pipeline : on la signale,
                # elle sera retentée à la prochaine exécution (le bloc est incrémental).
                # Vu le 2026-09-26 : un "400 Bad Request" passager du service IGN.
                print(f'  photo NON téléchargée pour {id_cavite} : {erreur}')
                echecs.append(id_cavite)
                continue
            s3.put_object(Bucket=BUCKET, Key=cle, Body=image, ContentType='image/jpeg')
            curseur.execute("""
                insert into silver.medias (cle, bucket, type_objet, id_objet, type_media,
                                           url_publique, source_url, licence, octets)
                values (%s, %s, 'cavite', %s, 'orthophoto', %s, %s, %s, %s)
                on conflict (cle) do nothing
            """, (cle, BUCKET, id_cavite, f'{URL_PUBLIQUE}/{BUCKET}/{cle}', url,
                  'IGN BD ORTHO — Licence Ouverte Etalab 2.0', len(image)))
            nouvelles += 1
            time.sleep(0.3)   # politesse envers le service de l'IGN
        print(f'{len(cavites)} cavités sur la carte : {nouvelles} photos téléchargées, '
              f'{len(cavites) - nouvelles - len(echecs)} déjà présentes, {len(echecs)} en échec')

        # Lien vers la photo dans chaque fiche MongoDB (réécrit à chaque passage :
        # le job Spark vide et réécrit la collection des fiches)
        curseur.execute("select id_objet, url_publique from silver.medias where type_media = 'orthophoto'")
        fiches = base_mongo()['cavites_fiches']
        for id_cavite, url_photo in curseur.fetchall():
            fiches.update_one({'_id': id_cavite}, {'$set': {'medias.photo_aerienne': url_photo}})
    connexion.close()

    # Quelques échecs isolés sont tolérés ; au-delà de 10 %, c'est un vrai problème (service IGN
    # en panne, réseau coupé...) : le bloc échoue pour qu'on le voie dans Mage.
    if cavites and len(echecs) > 0.1 * len(cavites):
        raise RuntimeError(f'{len(echecs)} photos sur {len(cavites)} en échec (plus de 10 %)')
