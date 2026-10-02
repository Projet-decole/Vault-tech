"""Lance le job Spark spark/jobs/clean_cavites.py → silver.cavites (cavités, coordonnées harmonisées)."""
from homepedia.utils.spark import spark_submit

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom


@custom
def run_clean_cavites(*args, **kwargs) -> None:
    spark_submit('clean_cavites.py')
