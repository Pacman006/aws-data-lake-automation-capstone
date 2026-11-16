"""Read the most recent telemetry reading behind Cognito-secured API Gateway."""

import json
import os
from decimal import Decimal

from shared.schema import DEVICE_ID


def response(status, payload):
    return {
        "statusCode": status,
        "headers": {"content-type": "application/json", "cache-control": "no-store"},
        "body": json.dumps(payload, default=lambda value: float(value) if isinstance(value, Decimal) else str(value)),
    }


def read_device(event, table):
    device_id = (event.get("pathParameters") or {}).get("device_id", "")
    if not DEVICE_ID.fullmatch(device_id):
        return response(400, {"message": "Invalid device_id"})
    item = table.get_item(Key={"device_id": device_id}, ConsistentRead=True).get("Item")
    if item is None:
        return response(404, {"message": "No reading found for this device"})
    return response(200, item)


def lambda_handler(event, context):
    import boto3

    table = boto3.resource("dynamodb").Table(os.environ["LATEST_TABLE_NAME"])
    return read_device(event, table)
