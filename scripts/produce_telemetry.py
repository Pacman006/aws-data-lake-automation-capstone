#!/usr/bin/env python3
"""Send example connected-vehicle readings to Kinesis (dry run by default)."""

import argparse
import json
import random
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from shared.schema import validate_record  # noqa: E402


def generate_events(count, device, seed=42):
    rng = random.Random(seed)
    start = datetime.now(timezone.utc).replace(microsecond=0) - timedelta(seconds=count - 1)
    for i in range(count):
        now = (start + timedelta(seconds=i)).isoformat().replace("+00:00", "Z")
        yield validate_record({
            "event_id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{device}:{now}:{i}")),
            "device_id": device,
            "event_time": now,
            "speed_kmh": round(rng.uniform(10, 95), 2),
            "fuel_percent": round(rng.uniform(20, 100), 2),
            "diagnostic_codes": [],
        })


def send_events(client, stream_name, events):
    sent = 0
    for event in events:
        payload = (json.dumps(event, separators=(",", ":")) + "\n").encode("utf-8")
        # Newline matters: Firehose joins incoming records in an S3 object.
        client.put_record(StreamName=stream_name, Data=payload, PartitionKey=event["device_id"])
        sent += 1
    return sent


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate sample telemetry, optionally publish to Kinesis")
    parser.add_argument("--stream-name", help="Kinesis Data Streams stream name")
    parser.add_argument("--region", default="ap-south-1", help="AWS region")
    parser.add_argument("--profile", help="Optional AWS CLI profile")
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--device", default="vehicle-001")
    parser.add_argument("--send", action="store_true", help="Actually send records to AWS")
    args = parser.parse_args(argv)
    if not 1 <= args.count <= 500:
        parser.error("--count must be between 1 and 500")
    try:
        events = list(generate_events(args.count, args.device))
    except ValueError as exc:
        parser.error(str(exc))
    if not args.send:
        print("DRY RUN: no AWS calls made. Add --send --stream-name NAME to publish.\n")
        for event in events:
            print(json.dumps(event))
        return 0
    if not args.stream_name:
        parser.error("--stream-name is required when using --send")
    import boto3

    client = boto3.Session(profile_name=args.profile, region_name=args.region).client("kinesis")
    print(f"Published {send_events(client, args.stream_name, events)} records to {args.stream_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
