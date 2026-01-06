"""
label_generation.py

Generates default labels for PD modelling using
engineered behavioural features.

This logic is rule-based, explainable, and intentionally noisy
to simulate real-world bank default definitions.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, rand

# -------- PATHS --------
FEATURE_PATH = "/workspaces/CRIS/cris/datalake/features/account_features_basic"
OUTPUT_PATH = "/workspaces/CRIS/cris/datalake/models/pd_training_dataset"


def build_spark():
    spark = (
        SparkSession.builder
        .appName("CRIS-PD-Label-Generation")
        .master("local[*]")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark


def main():
    spark = build_spark()

    # 1. Read engineered features
    features_df = spark.read.parquet(FEATURE_PATH)

    # 2. Generate default label (multi-signal, explainable rules)
    labeled_df = (
        features_df
        .withColumn(
            "default_flag",
            when(
                # High spend + inactivity → stress behaviour
                (col("recency_days_is_inactive_30d") == 1) &
                (col("spend_per_txn_30d") > 35000),
                1
            )
            .when(
                # Low engagement + large ticket sizes
                (col("txn_count_30d") <= 2) &
                (col("spend_per_txn_30d") > 40000) &
                (rand()<0.6),

                1
            )
            .otherwise(0)
        )
        .select(
            "account_id",
            "spend_30d",
            "txn_count_30d",
            "spend_per_txn_30d",
            "recency_days_is_inactive_30d",
            "default_flag"
        )
    )

    # 3. Write PD training dataset
    (
        labeled_df.write
        .mode("overwrite")
        .parquet(OUTPUT_PATH)
    )

    print("🟢 PD training dataset written to:", OUTPUT_PATH)
    spark.stop()


if __name__ == "__main__":
    main()
