#!/usr/bin/env python3
"""Run a Glue ETL job and optionally update the Athena table via its crawler."""
import argparse
import time


def wait_for_job(glue, job_name, run_id, timeout):
    start = time.monotonic()
    while time.monotonic() - start < timeout:
        status = glue.get_job_run(JobName=job_name, RunId=run_id)["JobRun"]["JobRunState"]
        print("Glue job:", status)
        if status == "SUCCEEDED":
            return
        if status in {"FAILED", "STOPPED", "TIMEOUT", "ERROR", "EXPIRED"}:
            raise RuntimeError(f"Glue job finished with status {status}")
        time.sleep(15)
    raise TimeoutError("Glue job did not finish within the configured timeout")


def wait_for_crawler(glue, name, timeout):
    start = time.monotonic()
    seen_running = False
    while time.monotonic() - start < timeout:
        crawler = glue.get_crawler(Name=name)["Crawler"]
        state = crawler["State"]
        print("Crawler:", state)
        if state == "RUNNING":
            seen_running = True
        if state == "READY" and (seen_running or crawler.get("LastCrawl")):
            crawl = crawler.get("LastCrawl", {})
            if crawl and crawl.get("Status") != "SUCCEEDED":
                raise RuntimeError(f"Crawler finished with status {crawl.get('Status')}")
            return
        time.sleep(10)
    raise TimeoutError("Crawler did not finish within the configured timeout")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job", required=True, help="GlueJobName output")
    parser.add_argument("--crawler", help="GlueCrawlerName output")
    parser.add_argument("--region", default="ap-south-1")
    parser.add_argument("--profile")
    parser.add_argument("--confirm-cost", action="store_true", help="Confirm you understand Glue incurs charges")
    args = parser.parse_args()
    if not args.confirm_cost:
        parser.error("Glue is billed. Add --confirm-cost after reviewing the AWS pricing.")
    import boto3

    glue = boto3.Session(profile_name=args.profile, region_name=args.region).client("glue")
    run = glue.start_job_run(JobName=args.job)
    print("Glue run ID:", run["JobRunId"])
    wait_for_job(glue, args.job, run["JobRunId"], 2400)
    if args.crawler:
        glue.start_crawler(Name=args.crawler)
        wait_for_crawler(glue, args.crawler, 1200)
    print("ETL finished. Check S3 curated data and Glue catalog before querying with Athena.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
