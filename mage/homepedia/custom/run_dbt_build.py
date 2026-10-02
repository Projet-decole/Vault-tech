"""Lance dbt : construit les modèles staging + gold, exécute tous les tests, puis régénère la doc.

Si un test échoue, dbt renvoie une erreur → le bloc échoue → la suite du pipeline ne tourne pas.
"""
import subprocess

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom

PROJET_DBT = '/home/src/homepedia/dbt/homepedia_dbt'


@custom
def run_dbt_build(*args, **kwargs) -> None:
    for commande in (['dbt', 'build'], ['dbt', 'docs', 'generate']):
        # --no-partial-parse : relit TOUS les fichiers du projet à chaque fois (~2 s).
        # Le cache d'analyse de dbt (target/partial_parse.msgpack) ne voyait pas certaines
        # modifications de fichiers YAML → 22 tests ignorés SANS aucun message d'erreur.
        commande += ['--project-dir', PROJET_DBT, '--profiles-dir', PROJET_DBT, '--no-partial-parse']
        print('$', ' '.join(commande))
        subprocess.run(commande, check=True, cwd=PROJET_DBT)
