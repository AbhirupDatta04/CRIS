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
        .withColumn(
            "recency_days_is_inactive_30d",
            when(col("recency_days") > 30, 
                    1
                ).otherwise(0)
        )
        .select(
            "account_id",
            "spend_30d",
            "txn_count_30d",
            "spend_per_txn_30d",
            "recency_days_is_inactive_30d"
        )
    )
    features_df.printSchema()
    feature_count = features_df.count()
    print("Feature Dataset Count:",feature_count)
    if feature_count == 0:
        raise Exception("CRIS-13 FAILED: Feature dataset is empty")

    TOTAL_ROWS = feature_count
    NULL_THRESHOLD = 0.05


    critical_columns = [
    "spend_30d",
    "txn_count_30d",
    "recency_days_is_inactive_30d"
    ]

    for c in critical_columns:
        null_count = features_df.filter(col(c).isNull()).count()
        print(f"Debug: Column '{c}' null count: {null_count}")
        null_ratio = null_count / TOTAL_ROWS
        print(f"Column '{c}' has {null_count} nulls out of {TOTAL_ROWS} rows (Null Ratio: {null_ratio:.2%})")
        if null_ratio > NULL_THRESHOLD:
            raise Exception(f"CRIS-13 FAILED: Column '{c}' has null ratio {null_ratio:.2%} exceeding threshold of {NULL_THRESHOLD:.2%}")
    

    # 1️⃣ Negative transaction counts
    invalid_txn_count = features_df.filter(col("txn_count_30d") < 0).count()
    if invalid_txn_count > 0:
        raise Exception(
        f"CRIS-13 FAILED: Negative txn_count_30d detected | rows={invalid_txn_count}"
        )

    # 2️⃣ Negative spend
    invalid_spend = features_df.filter(col("spend_30d") < 0).count()
    if invalid_spend > 0:
        raise Exception(
            f"CRIS-13 FAILED: Negative spend_30d detected | rows={invalid_spend}"
        )
    # 3️⃣ Negative spend per transaction
    invalid_spend_per_txn = features_df.filter(col("spend_per_txn_30d") < 0).count()
    if invalid_spend_per_txn > 0:
        raise Exception(
            f"CRIS-13 FAILED: Negative spend_per_txn_30d detected | rows={invalid_spend_per_txn}"
        )
    # 4️⃣ Invalid inactivity flag
    invalid_inactive_flag = features_df.filter(
        ~col("recency_days_is_inactive_30d").isin([0, 1])
    ).count()
    if invalid_inactive_flag > 0:
        raise Exception(
         f"CRIS-13 FAILED: Invalid recency_days_is_inactive_30d values detected | rows={invalid_inactive_flag}"
    )

    features_df.write.mode("overwrite").parquet(FEATURE_PATH)
    
    print("Basic Features for Account saved to Features Layer to",FEATURE_PATH)
    spark.stop()


if __name__ == "__main__":
    main()