# AWS deployment and acceptance evidence (fill after real testing)

> **Status: NOT TESTED.** Complete each field using your own AWS execution results. Never fabricate screenshots, IDs, performance improvements, costs or pass statuses.

## Deployment information

| Field | Observed value |
|---|---|
| Test date/time (UTC) | Not captured |
| AWS account (masked) | Not captured |
| Region | Not captured |
| Stack name and stack ID | Not captured |
| Git commit hash | Not captured |
| Change-set reviewer | Not captured |
| AWS Budget / cost estimate | Not captured |

## Acceptance tests

| ID | Test | Required evidence | Result |
|---|---|---|---|
| T01 | CloudFormation stack creates resources | CloudFormation events and outputs | Not run |
| T02 | Kinesis receives synthetic JSONL | Producer log and stream metrics | Not run |
| T03 | Firehose archives raw GZIP JSONL to S3 | S3 object properties and delivery log | Not run |
| T04 | Lambda validates record / rejects invalid field | Sanitized CloudWatch logs | Not run |
| T05 | DynamoDB latest-value replay protection | Before/after item inspection | Not run |
| T06 | Cognito/API Gateway rejects unauthenticated request | HTTP 401 screenshot/output | Not run |
| T07 | Authorized API GET returns latest record | HTTP 200 with synthetic data | Not run |
| T08 | Glue produces curated Parquet | Glue job run ID and curated S3 path | Not run |
| T09 | Glue crawler registers catalog table | Crawler run ID, table + partitions | Not run |
| T10 | Athena aggregate query succeeds | Query execution ID and scanned bytes | Not run |
| T11 | CloudWatch alarm / SNS notification tested | Alarm history and subscription receipt | Not run |
| T12 | Stack and retained resources cleaned up | AWS console/CLI verification | Not run |
| T13 | S3 cross-region DR and DynamoDB Global Tables | Controlled failover log, RPO/RTO | **Not implemented** |
| T14 | CodePipeline staged release + manual approval | Pipeline execution/audit record | **Not implemented** |

## Findings and remediation

| Observation / issue | Impact | Fix owner | Retest date | Status |
|---|---|---|---|---|
| None recorded | | | | |

## Sign-off

- Reviewer: __________________________
- Date: ______________________________
- Accepted scope: _____________________
- Open risks: _________________________
