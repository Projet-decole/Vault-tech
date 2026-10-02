"""Job Spark — petite synthèse par commune (jointure NON spatiale, pédagogique).

Lit   silver.parcelles et silver.cavites (PostgreSQL)
Écrit silver.stats_communes_brutes : nb de parcelles et nb de cavités par code INSEE.

Le vrai croisement « parcelle à moins de 200 m d'une cavité » se fera dans PostGIS (phase 5) :
ici on compte seulement par commune, pour voir un groupBy et une jointure dans Spark.
"""
from pyspark.sql import functions as F

from commun import ecrire_table, lire_table, session


def main():
    spark = session('stats_communes')

    # groupBy = SHUFFLE : Spark redistribue les lignes pour réunir celles d'une même commune
    parcelles = (lire_table(spark, 'silver.parcelles')
                 .groupBy('code_insee')
                 .agg(F.count('*').alias('nb_parcelles'),
                      F.sum('contenance_m2').alias('surface_cadastrale_m2')))
    cavites = (lire_table(spark, 'silver.cavites')
               .groupBy('code_insee')
               .agg(F.count('*').alias('nb_cavites'),
                    F.sum(F.when(F.col('type_cavite_code') == 'ouvrage militaire', 1).otherwise(0))
                     .alias('nb_ouvrages_militaires')))

    # Jointure "left" : on garde les communes du périmètre (celles qui ont des parcelles),
    # même sans aucune cavité (nb_cavites = 0 au lieu de NULL).
    stats = (parcelles.join(cavites, on='code_insee', how='left')
             .fillna(0, subset=['nb_cavites', 'nb_ouvrages_militaires']))

    ecrire_table(stats, 'silver.stats_communes_brutes')
    stats.orderBy('code_insee').show()  # 6 lignes : affichage sans risque
    spark.stop()


if __name__ == '__main__':
    main()
