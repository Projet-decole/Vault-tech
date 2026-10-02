"""Lance le job Spark spark/jobs/clean_cadastre.py → silver.parcelles (parcelles nettoyées)."""
from homepedia.utils.spark import spark_submit

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom


@custom
def run_clean_cadastre(*args, **kwargs) -> None:
    spark_submit('clean_cadastre.py')
