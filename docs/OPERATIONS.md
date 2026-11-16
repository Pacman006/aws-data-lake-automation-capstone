# Operations, monitoring and troubleshooting

## Daily health checklist for an AWS pilot

1. Confirm data is reaching the intended Kinesis stream; check incoming-record and write-throttle metrics.
2. Verify that Firehose is delivering objects to the private raw S3 bucket; inspect delivery errors and delivery delay.
3. Check processor Lambda `Errors`, `Throttles` and `Duration`; inspect iterator age for backlog.
4. Query DynamoDB `device_id` only in test environments that hold synthetic data.
5. Check last Glue run status, crawler run status and Athena catalog table freshness.
6. Review CloudWatch alarms and confirm SNS subscribers are receiving notifications.
7. Check current spend against the AWS Budget; idle Kinesis and retained data can still incur costs.

## Typical incident investigation

| Symptom | What to inspect first | Likely cause / next action |
|---|---|---|
| No raw S3 objects | Producer `--send`, Firehose stream state, CloudWatch delivery logs | Wrong stream name, IAM permissions, buffering, no records |
| Lambda returns errors | CloudWatch log group for processor | Permission, DynamoDB capacity, bad schema, runtime exception |
| DynamoDB shows older reading | Input timestamps and event order | Conditional update deliberately ignores older/equal records |
| Glue job cannot find script | Artifacts bucket path | Upload `glue/transform_telemetry.py` before first job run |
| No Athena table | Glue crawler state | Run ETL first, then crawler; check curated Parquet path |
| Athena has no rows | S3 curated data, crawler schema, results permissions | Source files missing/filtered; wrong table or database |
| API gives 401 | JWT issuer/audience/expiry and app client | Need Cognito access token from correct pool/client |
| API gives 404 | Device ID / DynamoDB item | Expected until a valid record has been processed |
| Stack deletion leaves S3 | Retained bucket and table policies | Intended data protection; clean up manually and carefully |

## Practical read-only AWS CLI checks

```bash
aws sts get-caller-identity
aws cloudformation describe-stacks --stack-name datasoftlake-dev --region ap-south-1
aws kinesis describe-stream-summary --stream-name REPLACE_WITH_STREAM --region ap-south-1
aws firehose describe-delivery-stream --delivery-stream-name REPLACE_WITH_DELIVERY --region ap-south-1
aws glue get-job --job-name REPLACE_WITH_JOB --region ap-south-1
aws cloudwatch describe-alarms --alarm-name-prefix datasoftlake-dev --region ap-south-1
```

## Incident ownership

| Severity | Example | Initial response |
|---|---|---|
| High | Raw data not landing for sustained period | Stop change rollout; inspect Firehose logs and Kinesis backlog |
| Medium | Glue run failure | Review job run logs, bookmark state and source data quality |
| Medium | API 401 failures for users | Verify Cognito configuration and token expiry; do not disable auth |
| Low | Single malformed event | Inspect validation warning and raw copy; correct producer schema |

## Validation after a change

Run unit tests, confirm CloudFormation change-set contents, deploy the smallest test environment, send synthetic telemetry, check DynamoDB and raw S3, execute Glue and crawler, query Athena and perform an authenticated API test. Record exact timestamps and IDs in the evidence template.

## Alerting limitations

The starter configures one Lambda error alarm and an SNS topic; **it does not include every metric listed above**. Before production use, add Firehose delivery failure, Kinesis throttling/iterator age, Glue failed runs, API 5xx and data freshness alarms with measurable thresholds and named responders.
