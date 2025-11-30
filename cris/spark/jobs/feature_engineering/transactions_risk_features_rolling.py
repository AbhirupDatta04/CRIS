"""
transactions_risk_features_rolling.py

Rolling-Window Risk Features for CRIS (Credit Risk Intelligence System).
Builds behavior-based sliding-window features from SILVER transaction data.

Run:
  cd /workspaces/CRIS/cris
  python3 spark/jobs/feature_engineering/transactions_risk_features_rolling.py
"""

from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import (
    col, sum as _sum, count as _count, avg as _avg,
    max as _max, min as _min, stddev_pop, lag,
    unix_timestamp, when
)

SILVER_PATH = "/workspaces/CRIS/cris/datalake/silver/transactions"
FEATURE_PATH = "/workspaces/CRIS/cris/datalake/gold/transactions_risk_features_rolling"


# ---------------------------------------------------
# 1. Spark Setup
# ---------------------------------------------------
def build_spark():
    spark = (
        SparkSession.builder
        .appName("CRIS-Transactions-Rolling-Window-Features")
        .master("local[*]")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark


# ---------------------------------------------------
# 2. Helpers
# ---------------------------------------------------
def add_unix_ts(df):
    # Use your existing event_timestamp column
    return df.withColumn("unix_ts", unix_timestamp(col("event_timestamp")).cast("long"))


def build_rolling_features(df):
    windows_days = [1, 7, 30, 90]
    windows_seconds = {d: d * 24 * 3600 for d in windows_days}

    base_window = Window.partitionBy("account_id").orderBy("unix_ts")

    df_feats = df

    # Rolling window features
    for d, secs in windows_seconds.items():
        w = base_window.rangeBetween(-secs, 0)
        sfx = f"{d}d"

        df_feats = (
            df_feats
            .withColumn(f"txn_count_{sfx}", _count("*").over(w))
            .withColumn(f"txn_sum_{sfx}", _sum("amount").over(w))
            .withColumn(f"txn_avg_{sfx}", _avg("amount").over(w))
            .withColumn(f"txn_stddev_{sfx}", stddev_pop("amount").over(w))
            .withColumn(f"txn_max_{sfx}", _max("amount").over(w))
            .withColumn(f"txn_min_{sfx}", _min("amount").over(w))
        )

    # Days since previous transaction
    df_feats = df_feats.withColumn("prev_ts", lag("unix_ts").over(base_window))
    df_feats = df_feats.withColumn(
        "days_since_prev_txn",
        (col("unix_ts") - col("prev_ts")) / 86400
    )

    # 7d/30d spend velocity ratio
    df_feats = df_feats.withColumn(
        "recent_7d_to_30d_ratio",
        when(col("txn_sum_30d").isNull() | (col("txn_sum_30d") == 0), None)
        .otherwise(col("txn_sum_7d") / col("txn_sum_30d"))
    )

    # Large transaction relative to 30d avg
    df_feats = df_feats.withColumn(
        "large_relative_30d",
        when(
            (col("txn_avg_30d").isNotNull()) &
            (col("amount") > 3 * col("txn_avg_30d")),
            1
        ).otherwise(0)
    )

    return df_feats


# ---------------------------------------------------
# 3. MAIN
# ---------------------------------------------------
def main():
    spark = build_spark()

    silver_df = spark.read.parquet(SILVER_PATH)

    # Select correct timestamp column: event_timestamp
    transactions = (
        silver_df
        .select("transaction_id", "account_id", "event_timestamp", "amount")
        .orderBy("account_id", "event_timestamp")
    )

    # Add unix_ts for time-based windows
    transactions = add_unix_ts(transactions)

    # Repartition by account
    transactions = transactions.repartition(100, "account_id")

    # Compute rolling features
    rolling_df = build_rolling_features(transactions)

    # Write output
    (
        rolling_df.write
        .mode("overwrite")
        .parquet(FEATURE_PATH)
    )

    print("✨ Rolling-Window Features written to:", FEATURE_PATH)
    spark.stop()


if __name__ == "__main__":
    main()
