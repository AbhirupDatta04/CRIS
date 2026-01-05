"""
transactions_gold_account_30d.py
"""

# spend_30d: total customer spending in last 30 days
# txn_count_30d: frequency of transactions (usage intensity)
# avg_amount_30d: average ticket size
# spend_volatility_30d: instability in spending behaviour
# recency_days: days since last observed transaction

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    sum as _sum,
    count as _count,
    avg as _avg,
    stddev as _stddev,
    countDistinct,
    max as _max,
    current_date,
    date_sub,
    datediff,
    when
)

SILVER_PATH = "/workspaces/CRIS/cris/datalake/silver/transactions"
GOLD_PATH = "/workspaces/CRIS/cris/datalake/gold/account_risk_30d"


def build_spark():
    spark = (
        SparkSession.builder
        .appName("CRIS-Gold-Account-Risk-30D")
        .master("local[*]")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark


def main():
    spark = build_spark()

    # 1. Read Silver transactions
    silver_df = spark.read.parquet(SILVER_PATH)

    # 2. Create event_time from Silver.timestamp
    silver_df = silver_df.withColumn(
        "event_time",
        col("timestamp").cast("timestamp")
    )

    # 3. Filter last 30 days of activity
    recent_df = silver_df.filter(
        col("event_time") >= date_sub(current_date(), 30)
    )
    recent_df = recent_df.filter(col("amount") > 0) #Changed as only positive amounts should be there for Risk


    # 4. Base behavioural aggregates (unchanged)
    gold_base_df = (
        recent_df
        .groupBy("account_id")
        .agg(
            _sum("amount").alias("spend_30d"),
            _count("*").alias("txn_count_30d"),
            _avg("amount").alias("avg_amount_30d"),
            _stddev("amount").alias("spend_volatility_30d"),
            countDistinct("merchant_id").alias("merchant_diversity_30d"),
            datediff(current_date(), _max("event_time")).alias("recency_days")
        )
    )

    # 5. Add LOW ACTIVITY FLAG (engagement risk)
    gold_with_activity_flag = gold_base_df.withColumn(
        "low_activity_flag_30d",
        when(col("txn_count_30d") <= 2, 1).otherwise(0)
    )

    # 6. Join average transaction amount back to transaction level
    txn_with_avg_df = recent_df.join(
        gold_base_df.select("account_id", "avg_amount_30d"),
        on="account_id",
        how="left"
        )

    # 7. Flag high-value transactions (relative threshold)
    txn_flagged_df = txn_with_avg_df.withColumn(
        "is_high_value_txn",
        when(col("amount") >= 2 * col("avg_amount_30d"), 1).otherwise(0)
    )
    # 8. Compute high-value transaction ratio per account
    high_value_ratio_df = (
        txn_flagged_df
        .groupBy("account_id")
        .agg(
        (_sum("is_high_value_txn") / _count("*"))
        .alias("high_value_txn_ratio_30d")
        )
        )

    # 9. Final Gold table (safe join)
    gold_df = (
        gold_with_activity_flag
        .join(high_value_ratio_df, on="account_id", how="left")
        .fillna({"high_value_txn_ratio_30d": 0.0})
    )
    # 8. Write Gold dataset
    (
        gold_df.write
        .mode("overwrite")
        .parquet(GOLD_PATH)
    )

    print("🟡 Enhanced Gold risk dataset written to:", GOLD_PATH)
    spark.stop()


if __name__ == "__main__":
    main()
