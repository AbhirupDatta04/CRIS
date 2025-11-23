"""
transactions_risk_features_daily.py

Daily Risk Feature Engineering for CRIS (Credit Risk Intelligence System).
Transforms GOLD daily aggregates + SILVER transactions into
behavioral, category and velocity-based risk features.

Run:
  cd /workspaces/CRIS/cris
  python3 spark/jobs/feature_engineering/transactions_risk_features_daily.py
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, countDistinct, sum as _sum,
    count as _count, max as _max, min as _min
)

# Input GOLD table: daily customer spend aggregates
GOLD_PATH = "/workspaces/CRIS/cris/datalake/gold/transactions_daily_customer_spend"

# Input SILVER table: cleaned transaction-level data
SILVER_PATH = "/workspaces/CRIS/cris/datalake/silver/transactions"

# Output feature store table
FEATURE_PATH = "/workspaces/CRIS/cris/datalake/gold/transactions_risk_features_daily"


def build_spark():
    spark = (
        SparkSession.builder
        .appName("CRIS-Transactions-Daily-Risk-Features")
        .master("local[*]")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark


def main():
    spark = build_spark()

    # ---------------------------------------------------
    # 1. LOAD INPUT TABLES
    # ---------------------------------------------------
    gold_df = spark.read.parquet(GOLD_PATH)
    silver_df = spark.read.parquet(SILVER_PATH)

    # ---------------------------------------------------
    # 2. MERCHANT DIVERSITY + BASIC AGGREGATIONS
    # ---------------------------------------------------
    merchant_features = (
        silver_df.groupBy("account_id", "event_date")
        .agg(
            countDistinct("merchant_id").alias("merchant_diversity"),
            _count("*").alias("transaction_count_day"),
            _sum("amount").alias("total_amount_day")
        )
    )

    # ---------------------------------------------------
    # 3. CATEGORY RATIOS (Food, Ecommerce, ATM)
    # ---------------------------------------------------
    merchant_categorized = (
        silver_df.withColumn(
            "is_food",
            col("merchant_id").isin("SWIGGY", "ZOMATO").cast("int")
        )
        .withColumn(
            "is_ecommerce",
            col("merchant_id").isin("AMAZON", "FLIPKART").cast("int")
        )
        .withColumn(
            "is_atm",
            (col("transaction_type") == "ATM").cast("int")
        )
    )

    category_features = (
        merchant_categorized.groupBy("account_id", "event_date")
        .agg(
            _sum("is_food").alias("food_txn_count"),
            _sum("is_ecommerce").alias("ecom_txn_count"),
            _sum("is_atm").alias("atm_txn_count"),
            _count("*").alias("total_txn_count_cat")
        )
    )

    category_features = (
        category_features
            .withColumn("food_ratio", col("food_txn_count") / col("total_txn_count_cat"))
            .withColumn("ecom_ratio", col("ecom_txn_count") / col("total_txn_count_cat"))
            .withColumn("atm_ratio", col("atm_txn_count") / col("total_txn_count_cat"))
    )

    # ---------------------------------------------------
    # 4. MAX & MIN SPEND PER DAY
    # ---------------------------------------------------
    amount_stats = (
        silver_df.groupBy("account_id", "event_date")
        .agg(
            _max("amount").alias("max_transaction_amount"),
            _min("amount").alias("min_transaction_amount")
        )
    )

    # ---------------------------------------------------
    # 5. JOIN ALL FEATURE SETS INTO A SINGLE TABLE
    # ---------------------------------------------------
    features_df = (
        gold_df
        .join(merchant_features, ["account_id", "event_date"], "left")
        .join(category_features, ["account_id", "event_date"], "left")
        .join(amount_stats, ["account_id", "event_date"], "left")
    )

    # ---------------------------------------------------
    # 6. SAVE OUTPUT TO FEATURE STORE
    # ---------------------------------------------------
    (
        features_df.write
        .mode("overwrite")
        .parquet(FEATURE_PATH)
    )

    print("✨ Daily Risk Features written to:", FEATURE_PATH)
    spark.stop()


if __name__ == "__main__":
    main()
