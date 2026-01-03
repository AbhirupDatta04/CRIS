"""
label_generation.py

For PD modelling using account features and creating a default flag label to understand and compute the probability of default.
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, 
    when,
    round
)

FEATURE_PATH= "/workspaces/CRIS/cris/datalake/features/account_features_basic"  
PD_MODEL_PATH = "/workspaces/CRIS/cris/datalake/models/pd_training_dataset"


def build_spark():
    spark = (
        SparkSession.builder
        .appName("CRIS-Models-PD-Label-Generation")
        .master("local[*]")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark

def main():
    spark=build_spark()

    features_df = spark.read.parquet(FEATURE_PATH)

    pd_label_generation_df=(
        features_df
        .withColumn(
        "default_flag",
        when(
                (col("spend_per_txn_30d") > 42000) & (col("txn_count_30d") < 5),
                1
            ).otherwise(0)
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

    pd_label_generation_df.write.mode("overwrite").parquet(PD_MODEL_PATH)
    
    print("PD for Account saved to Features Layer to",PD_MODEL_PATH)
    spark.stop()


if __name__ == "__main__":
    main()