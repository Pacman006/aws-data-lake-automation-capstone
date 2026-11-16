"""AWS Glue Spark job: raw JSONL from Firehose -> partitioned Parquet in S3.

Run this script only on AWS Glue. It requires the AWS Glue runtime (not a
normal local Python environment).
"""

import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import col, to_date, to_timestamp

args = getResolvedOptions(sys.argv, ["JOB_NAME", "RAW_BUCKET", "CURATED_BUCKET"])
sc = SparkContext.getOrCreate()
glue = GlueContext(sc)
job = Job(glue)
job.init(args["JOB_NAME"], args)

# The transformation context lets AWS Glue bookmarks track input files.
raw = glue.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={"paths": [f"s3://{args['RAW_BUCKET']}/raw/"], "recurse": True},
    format="json",
    transformation_ctx="raw_events",
)

if raw.count() > 0:
    frame = raw.toDF()
    required = {"event_id", "device_id", "event_time", "speed_kmh", "fuel_percent"}
    if not required.issubset(set(frame.columns)):
        raise ValueError(f"Raw data is missing columns: {sorted(required - set(frame.columns))}")

    clean = (
        frame
        .withColumn("event_timestamp", to_timestamp(col("event_time")))
        .filter(col("event_id").isNotNull() & col("device_id").isNotNull())
        .filter(col("event_timestamp").isNotNull())
        .filter(col("speed_kmh").between(0, 300) & col("fuel_percent").between(0, 100))
        .dropDuplicates(["event_id"])
        .withColumn("event_date", to_date(col("event_timestamp")))
    )
    (
        clean.write.mode("append")
        .partitionBy("event_date")
        .parquet(f"s3://{args['CURATED_BUCKET']}/telemetry/")
    )

job.commit()
