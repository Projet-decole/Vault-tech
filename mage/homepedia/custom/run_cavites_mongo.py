"""Lance le job Spark spark/jobs/cavites_vers_mongo.py → MongoDB homepedia.cavites_fiches (fiches complètes)."""
from homepedia.utils.spark import spark_submit

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom


@custom
def run_cavites_mongo(*args, **kwargs) -> None:
    spark_submit('cavites_vers_mongo.py')
