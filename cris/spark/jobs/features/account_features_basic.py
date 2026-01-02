"""
account_features_basic.py

This is for feautures which are derived from the gold transactions over 30 days
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, 
    when,
    round
)

GOLD_PATH = "/workspaces/CRIS/cris/datalake/gold/account_risk_30d"
FEATURE_PATH=   "/workspaces/CRIS/cris/datalake/features/account_features_basic"  


def build_spark():
    spark = (
        SparkSession.builder
        .appName("CRIS-Features-Account-Features-Basic")
        .master("local[*]")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark

def main():
    spark=build_spark()

    gold_df = spark.read.parquet(GOLD_PATH)

    features_df=(
        gold_df
        .withColumn(
        "spend_per_txn_30d",
        when(col("txn_count_30d")>0,
            round(col("spend_30d")/col("txn_count_30d"),2)
            ).otherwise(0)
        )
        .select(
            "account_id",
            "spend_30d",
            "txn_count_30d",
            "spend_per_txn_30d"
        )
    )

    features_df.write.mode("overwrite").parquet(FEATURE_PATH)
    
    print("Basic Features for Account saved to Features Layer to",FEATURE_PATH)
    spark.stop()


if __name__ == "__main__":
    main()