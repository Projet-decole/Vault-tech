"""Connexions aux bases, partagées par les blocs Mage (identifiants lus dans le .env)."""
import os

import psycopg2
import pymongo


def connexion_postgres():
    return psycopg2.connect(
        host='postgres',
        dbname=os.environ['POSTGRES_DB'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASSWORD'],
    )


def base_mongo():
    """Base MongoDB "homepedia" (le compte root est déclaré dans la base "admin")."""
    client = pymongo.MongoClient(
        'mongo', 27017,
        username=os.environ['MONGO_ROOT_USER'],
        password=os.environ['MONGO_ROOT_PASSWORD'],
        authSource='admin',
    )
    return client['homepedia']
