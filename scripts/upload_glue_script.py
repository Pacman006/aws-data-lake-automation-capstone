#!/usr/bin/env python3
"""Upload the Glue ETL program to the artifact bucket created by CloudFormation."""
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bucket", required=True, help="ArtifactBucketName stack output")
    parser.add_argument("--region", default="ap-south-1")
    parser.add_argument("--profile")
    args = parser.parse_args()
    import boto3

    source = Path(__file__).resolve().parents[1] / "glue" / "transform_telemetry.py"
    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    session.client("s3").upload_file(str(source), args.bucket, "glue/transform_telemetry.py")
    print(f"Uploaded {source.name} to s3://{args.bucket}/glue/transform_telemetry.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
