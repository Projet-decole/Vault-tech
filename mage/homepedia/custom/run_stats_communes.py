"""Lance le job Spark spark/jobs/stats_communes.py → silver.stats_communes_brutes (comptages par commune)."""
from homepedia.utils.spark import spark_submit

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom


@custom
def run_stats_communes(*args, **kwargs) -> None:
    spark_submit('stats_communes.py')
