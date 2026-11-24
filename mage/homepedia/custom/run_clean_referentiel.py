"""Lance le job Spark spark/jobs/clean_referentiel.py → silver.ref_* (régions, départements, communes)."""
from homepedia.utils.spark import spark_submit

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom


@custom
def run_clean_referentiel(*args, **kwargs) -> None:
    spark_submit('clean_referentiel.py')
