"""Kinesis consumer: validates telemetry and keeps each device's latest reading."""

import base64
import json
import logging
import os
from datetime import datetime, timezone
from decimal import Decimal

from shared.schema import InvalidTelemetry, validate_record

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def store_latest(table, event):
    """Only replace a reading with a strictly newer one.

    Kinesis/Lambda can deliver a record more than once. DynamoDB's condition
    makes replaying a previously processed event harmless.
    """
    from botocore.exceptions import ClientError

    item = {
        "device_id": event["device_id"],
        "event_id": event["event_id"],
        "event_time": event["event_time"],
        "speed_kmh": Decimal(str(event["speed_kmh"])),
        "fuel_percent": Decimal(str(event["fuel_percent"])),
        "diagnostic_codes": event["diagnostic_codes"],
        "processed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    try:
        table.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(device_id) OR event_time < :new_time",
            ExpressionAttributeValues={":new_time": event["event_time"]},
        )
        return True
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
            return False
        raise


def process_batch(event, table):
    """Return Lambda's partial-batch response for retryable failures."""
    failures = []
    for record in event.get("Records", []):
        sequence_number = record.get("kinesis", {}).get("sequenceNumber", "")
        try:
            raw = base64.b64decode(record["kinesis"]["data"]).decode("utf-8")
            cleaned = validate_record(json.loads(raw.strip()))
        except (KeyError, UnicodeError, ValueError, InvalidTelemetry) as exc:
            # Reject malformed records; retrying a permanently invalid message
            # will not repair it. The raw copy is retained by Firehose in S3.
            logger.warning("Discarded invalid telemetry record: %s", exc)
            continue
        try:
            store_latest(table, cleaned)
        except Exception:
            logger.exception("Failed to save reading for %s", cleaned["device_id"])
            if sequence_number:
                failures.append({"itemIdentifier": sequence_number})
    return {"batchItemFailures": failures}


def lambda_handler(event, context):
    import boto3

    table = boto3.resource("dynamodb").Table(os.environ["LATEST_TABLE_NAME"])
    return process_batch(event, table)
