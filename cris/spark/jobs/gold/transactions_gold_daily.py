"""
transactions_gold_daily.py

Reads SILVER transactions and creates a GOLD table:
daily total spend per customer.

Run:
  cd /workspaces/CRIS/cris
  python3 spark/jobs/gold/transactions_gold_daily.py
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, count as _count, avg as _avg

SILVER_PATH = "/workspaces/CRIS/cris/datalake/silver/transactions"
GOLD_PATH = "/workspaces/CRIS/cris/datalake/gold/transactions_daily_customer_spend"


def build_spark():
    spark = (
        SparkSession.builder
        .appName("CRIS-Transactions-Gold-Daily")
        .master("local[*]")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark


def main():
    spark = build_spark()

    # 1) Read cleaned SILVER transactions
    silver_df = spark.read.parquet(SILVER_PATH)

    # We assume silver_df has at least:
    # account_id (int), event_date (date), amount (double)

    # 2) Group by customer + date and aggregate
    gold_df = (
        silver_df
        .groupBy("account_id", "event_date")
        .agg(
            _sum(col("amount")).alias("total_spend"),
            _count("*").alias("transaction_count"),
            _avg(col("amount")).alias("avg_transaction_amount")
        )
    )

    # 3) Write the GOLD table
    (
        gold_df.write
        .mode("overwrite")   # overwrite for now (easy while developing)
        .parquet(GOLD_PATH)
    )

    print("🟡 Gold table written to:", GOLD_PATH)
    spark.stop()


if __name__ == "__main__":
    main()
