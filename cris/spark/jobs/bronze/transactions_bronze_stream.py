"""
transactions_bronze_stream.py
Reads JSON transactions from Kafka and writes them to the RAW ZONE as Parquet.

Run:
  cd /workspaces/CRIS/cris
  python3 spark/jobs/bronze/transactions_bronze_stream.py
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, current_timestamp
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType

# ----- CONFIG -----
KAFKA_BOOTSTRAP = "localhost:9092"
KAFKA_TOPIC = "transactions"

OUTPUT_PATH = "/workspaces/CRIS/cris/datalake/raw/transactions"  # Parquet folder

# ----- TRANSACTION SCHEMA -----
transactions_schema = StructType([
    StructField("transaction_id", IntegerType(), False),
    StructField("account_id", IntegerType(), False),
    StructField("amount", DoubleType(), True),
    StructField("merchant_id", StringType(), True),
    StructField("transaction_type", StringType(), True),
    StructField("timestamp", StringType(), True),
])


def build_spark():
    spark = (
        SparkSession.builder
        .appName("CRIS-Transactions-Bronze")
        .master("local[*]")
        # Only Kafka needed here, no Delta
        .config(
            "spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0"
        )
        .config("spark.jars.ivy", "/tmp/.ivy")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark


def main():
    spark = build_spark()

    # --- READ FROM KAFKA ---
    raw_kafka_df = (
        spark.read
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP)
        .option("subscribe", KAFKA_TOPIC)
        .option("startingOffsets", "earliest")
        .load()
    )

    # Convert Kafka bytes → JSON → columns
    parsed_df = raw_kafka_df.select(
        from_json(col("value").cast("string"), transactions_schema).alias("data")
    ).select("data.*")

    # Add ingestion timestamp
    bronze_df = parsed_df.withColumn("ingested_at", current_timestamp())

    # --- WRITE AS PARQUET (RAW/BRONZE) ---
    (
        bronze_df.write
        .mode("append")
        .parquet(OUTPUT_PATH)
    )

    print("🟢 Bronze (Parquet) write complete at:", OUTPUT_PATH)
    spark.stop()


if __name__ == "__main__":
    main()
