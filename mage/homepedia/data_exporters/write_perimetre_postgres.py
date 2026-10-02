"""Bloc — Recopie la liste des communes (config/perimetre.yml) dans silver.perimetre_communes.

Ce n'est pas une donnée "source" (pas de bronze/Spark) : c'est notre configuration,
dont dbt a besoin pour afficher les noms de communes dans le gold.
"""
import os

import pandas as pd
import psycopg2

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def write_perimetre_postgres(perimetre: pd.DataFrame, *args, **kwargs) -> None:
    connexion = psycopg2.connect(
        host='postgres',
        dbname=os.environ['POSTGRES_DB'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASSWORD'],
    )
    # "with connexion" = une transaction : tout est validé à la fin, ou rien en cas d'erreur
    with connexion, connexion.cursor() as curseur:
        curseur.execute("""
            create table if not exists silver.perimetre_communes (
                code_insee  text primary key,
                nom         text not null,
                departement text not null
            )
        """)
        # truncate plutôt que drop : les vues dbt qui lisent cette table restent valides
        curseur.execute('truncate silver.perimetre_communes')
        curseur.executemany(
            'insert into silver.perimetre_communes (code_insee, nom, departement) values (%s, %s, %s)',
            perimetre[['insee', 'nom', 'departement']].itertuples(index=False, name=None),
        )
    connexion.close()
    print(f'silver.perimetre_communes : {len(perimetre)} communes')
