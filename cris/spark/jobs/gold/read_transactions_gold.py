"""
read_transactions_gold.py

Reads and prints the GOLD: transactions_daily_customer_spend
"""

from pyspark.sql import SparkSession

GOLD_PATH = "/workspaces/CRIS/cris/datalake/gold/transactions_daily_customer_spend"


def main():
    spark = (
        SparkSession.builder
        .appName("CRIS-Read-Gold")
        .master("local[*]")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    print("📂 Reading GOLD table from:", GOLD_PATH)
    df = spark.read.parquet(GOLD_PATH)

    print("\n🔎 Showing first 3 rows:\n")
    df.show(3, truncate=False)

    print("\n📏 Total rows:", df.count())
    spark.stop()


if __name__ == "__main__":
    main()
