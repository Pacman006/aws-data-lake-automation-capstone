#!/usr/bin/env python3
"""Run a read-only Athena query against the Glue catalog (opt-in due to cost)."""
import argparse
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", required=True)
    parser.add_argument("--results-bucket", required=True, help="Artifact bucket for query output")
    parser.add_argument("--table", default="telemetry", help="Check crawler-created table name in Glue first")
    parser.add_argument("--region", default="ap-south-1")
    parser.add_argument("--profile")
    parser.add_argument("--execute", action="store_true", help="Run the billable Athena query")
    args = parser.parse_args()
    if not all(c.isalnum() or c == "_" for c in args.table + args.database):
        parser.error("Database/table must contain only letters, numbers and underscores")
    sql = f'SELECT device_id, COUNT(*) AS events FROM "{args.table}" GROUP BY device_id ORDER BY events DESC LIMIT 20'
    if not args.execute:
        print("DRY RUN - Athena query will not execute unless --execute is supplied.\n", sql)
        return 0
    import boto3

    client = boto3.Session(profile_name=args.profile, region_name=args.region).client("athena")
    started = client.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={"Database": args.database},
        ResultConfiguration={"OutputLocation": f"s3://{args.results_bucket}/athena-results/"},
    )
    query_id = started["QueryExecutionId"]
    print("Query ID:", query_id)
    for _ in range(60):
        result = client.get_query_execution(QueryExecutionId=query_id)["QueryExecution"]
        state = result["Status"]["State"]
        if state in ("SUCCEEDED", "FAILED", "CANCELLED"):
            break
        time.sleep(2)
    else:
        raise TimeoutError("Athena query is still running; check it in the console")
    if state != "SUCCEEDED":
        raise RuntimeError(result["Status"].get("StateChangeReason", state))
    for row in client.get_query_results(QueryExecutionId=query_id)["ResultSet"]["Rows"]:
        print(" | ".join(col.get("VarCharValue", "") for col in row["Data"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
