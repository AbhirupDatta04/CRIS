from pyspark.sql import SparkSession

def preview_parquet(path, n=5):
    spark = (
        SparkSession.builder
        .appName("Preview-Parquet")
        .master("local[*]")
        .getOrCreate()
    )

    df = spark.read.parquet(path)
    df.show(n, truncate=False)

    spark.stop()


if __name__ == "__main__":
    # CHANGE this path to whatever you want to inspect
    preview_parquet("/workspaces/CRIS/cris/datalake/gold/transactions_risk_features_daily")
