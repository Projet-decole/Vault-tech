"""Job Spark — bronze → silver : référentiel géographique de la France (régions, départements, communes).

Lit   hdfs://namenode:8020/bronze/cog/dep=FR/...       (COG INSEE 2026, une ligne = une ligne du CSV)
      hdfs://namenode:8020/bronze/contours/dep=FR/...  (contours Etalab simplifiés à 100 m)
Écrit silver.ref_regions, silver.ref_departements, silver.ref_communes (nom, rattachement, contour)
      silver.ref_correspondance_communes (tout code commune connu → commune actuelle)

Pourquoi une table de correspondance : les sources n'ont pas toutes le même millésime. Une cavité
recensée en 2010 porte peut-être le code d'une commune fusionnée depuis, et le cadastre de Lyon est
découpé par arrondissement (69381...). Sans correspondance, ces lignes disparaîtraient des agrégats.
Règles reprises de Frank (pipeline/cleaning/geo.py, branche feature/indicateurs-prix-loyers) :
  - commune de plein exercice (COM)          → elle-même
  - arrondissement municipal (ARM)           → sa commune (COMPARENT), Lyon 1er → Lyon
  - commune associée ou déléguée (COMA/COMD) → sa commune nouvelle, sauf si elle garde le même code
"""
from pyspark.sql import functions as F
from pyspark.sql import types as T

from commun import ecrire_table, lire_bronze, session

CHAMPS_COG = ['niveau', 'TYPECOM', 'COM', 'REG', 'DEP', 'LIBELLE', 'COMPARENT', '_ingested_at']
SCHEMA_COG = T.StructType([T.StructField(c, T.StringType()) for c in CHAMPS_COG])

CHAMPS_CONTOURS = ['niveau', 'code', 'nom', 'geometrie_geojson']
SCHEMA_CONTOURS = T.StructType([T.StructField(c, T.StringType()) for c in CHAMPS_CONTOURS])


def main():
    spark = session('clean_referentiel')
    # Le dossier HDFS dep=FR crée une colonne "dep" ; sans sensibilité à la casse, Spark la confond
    # avec la colonne "DEP" du COG et tous les départements valent "FR" (vécu le 24/11).
    spark.conf.set('spark.sql.caseSensitive', 'true')
    cog =lire_bronze(spark, 'cog', SCHEMA_COG).cache()
    contours = lire_bronze(spark, 'contours', SCHEMA_CONTOURS).cache()

    def contour(niveau: str, cle: str):
        return (contours.filter(F.col('niveau') == niveau)
                .select(F.col('code').alias(cle), 'geometrie_geojson'))

    regions = (cog.filter(F.col('niveau') == 'region')
               .select(F.col('REG').alias('code_region'), F.col('LIBELLE').alias('nom'))
               .join(contour('regions', 'code_region'), 'code_region', 'left'))

    departements = (cog.filter(F.col('niveau') == 'departement')
                    .select(F.col('DEP').alias('code_departement'), F.col('LIBELLE').alias('nom'),
                            F.col('REG').alias('code_region'))
                    .join(contour('departements', 'code_departement'), 'code_departement', 'left'))

    communes_cog = cog.filter(F.col('niveau') == 'commune')
    communes = (communes_cog.filter(F.col('TYPECOM') == 'COM')
                .select(F.col('COM').alias('code_insee'), F.col('LIBELLE').alias('nom'),
                        F.col('DEP').alias('code_departement'), F.col('REG').alias('code_region'))
                .join(contour('communes', 'code_insee'), 'code_insee', 'left'))

    actuelles = communes_cog.filter(F.col('TYPECOM') == 'COM').select(F.col('COM').alias('code'))
    correspondance = (
        actuelles.withColumn('code_insee', F.col('code')).withColumn('type_code', F.lit('COM'))
        .unionByName(communes_cog.filter(F.col('TYPECOM') == 'ARM')
                     .select(F.col('COM').alias('code'), F.col('COMPARENT').alias('code_insee'),
                             F.lit('ARM').alias('type_code')))
        .unionByName(communes_cog.filter(F.col('TYPECOM').isin('COMA', 'COMD'))
                     .select(F.col('COM').alias('code'), F.col('COMPARENT').alias('code_insee'),
                             F.col('TYPECOM').alias('type_code'))
                     # jointure sur le NOM de colonne : évite l'ambiguïté d'une table jointe à elle-même
                     .join(actuelles, 'code', 'left_anti'))
        .dropDuplicates(['code']))

    for df, table in [(regions, 'silver.ref_regions'), (departements, 'silver.ref_departements'),
                      (communes, 'silver.ref_communes'),
                      (correspondance, 'silver.ref_correspondance_communes')]:
        df = df.cache()
        ecrire_table(df, table)
        sans_contour = df.filter('geometrie_geojson IS NULL').count() if 'geometrie_geojson' in df.columns else 0
        print(f'{table} : {df.count()} lignes' + (f', dont {sans_contour} sans contour' if sans_contour else ''))

    spark.stop()


if __name__ == '__main__':
    main()
