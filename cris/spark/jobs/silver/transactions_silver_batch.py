"""
transactions_silver_batch.py
Reads raw Parquet files from Bronze (RAW ZONE) and writes cleaned SILVER data.

Run:
  cd /workspaces/CRIS/cris
  python3 spark/jobs/silver/transactions_silver_batch.py
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, to_timestamp, to_date, hour, when
)

RAW_PATH = "/workspaces/CRIS/cris/datalake/raw/transactions"
SILVER_PATH = "/workspaces/CRIS/cris/datalake/silver/transactions"


def build_spark():
    spark = (
        SparkSession.builder
        .appName("CRIS-Transactions-Silver")
        .master("local[*]")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark


def main():
    spark = build_spark()

    # STEP 1: READ RAW DATA
    raw_df = spark.read.parquet(RAW_PATH)

    # STEP 2: CLEAN & TRANSFORM
    silver_df = (
        raw_df
        # Convert timestamp string → real timestamp
        .withColumn("event_timestamp", to_timestamp(col("timestamp")))
        
        # Convert amount to float (Spark already infers float but this is standard)
        .withColumn("amount", col("amount").cast("double"))

        # Derived columns
        .withColumn("event_date", to_date(col("event_timestamp")))
        .withColumn("event_hour", hour(col("event_timestamp")))
        .withColumn(
            "is_weekend",
            when(col("event_date").isin("Saturday", "Sunday"), True).otherwise(False)
        )
    )

    # STEP 3: WRITE TO SILVER
    (
        silver_df.write
        .mode("overwrite")
        .parquet(SILVER_PATH)
    )

    print("🟢 Silver layer written to:", SILVER_PATH)
    spark.stop()


if __name__ == "__main__":
    main()
