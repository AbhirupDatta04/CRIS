from pyspark.sql import SparkSession
import sys

spark=SparkSession.builder.master("local[*]").getOrCreate()
df=spark.read.parquet(sys.argv[1])
df.show(20,truncate=False)
df.printSchema()