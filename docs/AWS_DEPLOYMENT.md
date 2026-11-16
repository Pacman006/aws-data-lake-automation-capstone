# AWS deployment guide - controlled pilot

This guide is for a **temporary AWS pilot**. It describes actions that create paid AWS resources. It is not a guarantee that this repository has been deployed successfully in your account. Keep your region, stack name, account number and actual test results in the [deployment evidence worksheet](../reports/AWS_EVIDENCE_TEMPLATE.md).

## 1. Before deploying

1. Use an AWS account or sandbox you are authorized to manage. Set an **AWS Budget** and billing alert first.
2. Choose a region (example: `ap-south-1`, Mumbai). Confirm the services in the template are offered there.
3. Install **Python 3.12**, AWS CLI v2, AWS SAM CLI, and Git. Docker is optional for local tests. Installers: [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) | [SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html).
4. Prefer IAM Identity Center, a named AWS CLI profile or a short-lived deployment role. Do not save permanent keys in the repository.
5. Run offline tests and check every source screenshot for account details before publishing publicly.

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python scripts/check_project.py
python scripts/preflight.py
aws configure list
aws sts get-caller-identity
```

**Review IAM permissions** in `cloudformation/template.yaml`, especially the Firehose role, Glue service role and the Cognito user pool. CloudFormation deployment requires permission to create IAM roles and managed service resources.

## 2. Build and deploy CloudFormation/SAM

The script runs `aws sts get-caller-identity`, asks you to type `DEPLOY`, builds Lambda artifacts and deploys the stack with an AWS CloudFormation change set that requires confirmation.

**Linux, macOS, WSL or Git Bash:**

```bash
export AWS_REGION=ap-south-1
export ENVIRONMENT=dev
export PROJECT_PREFIX=datasoftlake
bash scripts/deploy.sh
```

**Windows PowerShell:**

```powershell
$env:AWS_REGION = 'ap-south-1'
$env:ENVIRONMENT = 'dev'
$env:PROJECT_PREFIX = 'datasoftlake'
.\scripts\deploy.ps1
```

The default CloudFormation stack name is `datasoftlake-dev`. Record stack outputs with:

```bash
aws cloudformation describe-stacks \
  --region ap-south-1 \
  --stack-name datasoftlake-dev \
  --query 'Stacks[0].Outputs' --output table
```

Expected outputs include `RawBucketName`, `CuratedBucketName`, `ArtifactBucketName`, `TelemetryStreamName`, `LatestTableName`, `GlueJobName`, `GlueCrawlerName`, `GlueDatabaseName`, `ApiUrl`, `CognitoUserPoolId`, and `CognitoClientId`. **These are example output keys, not invented deployed resource IDs.**

### What will cost money?

A provisioned Kinesis shard, Data Firehose delivery, S3 storage/requests, DynamoDB requests/PITR, Lambda execution, Glue workers and crawler runs, Athena bytes scanned, logs and notifications. Even an idle stream can incur charges. Avoid long-running stacks when you are not testing.

## 3. Upload the Glue ETL file

CloudFormation creates a Glue job *definition*, but the Spark script must be uploaded to the artifact bucket after the stack exists. Copy `ArtifactBucketName` from the stack outputs:

```bash
python scripts/upload_glue_script.py --bucket REPLACE_WITH_ARTIFACT_BUCKET --region ap-south-1
```

Expected: `s3://.../glue/transform_telemetry.py` is visible in the S3 console. No job has run yet.

## 4. Send a few synthetic records

A dry run prints records without contacting AWS:

```bash
python scripts/produce_telemetry.py --count 3
```

Actual ingestion (replace with the `TelemetryStreamName` output):

```bash
python scripts/produce_telemetry.py \
  --stream-name REPLACE_WITH_STREAM_NAME \
  --region ap-south-1 --count 5 --send
```

If you use a named AWS profile, add `--profile YOUR_PROFILE`. Wait for Data Firehose's configured buffering interval and check the raw bucket prefix `raw/` in S3. There is no promise of immediate delivery; watch Firehose metrics and errors in CloudWatch if the objects do not arrive.

## 5. Check the operational view in DynamoDB

In AWS Console open **DynamoDB → Tables →** your `LatestTableName` → **Explore items**. The expected key is `device_id`. Each device should show its most recent valid timestamp, speed and fuel percentage. You can also use:

```bash
aws dynamodb get-item \
  --region ap-south-1 \
  --table-name REPLACE_WITH_LATEST_TABLE \
  --key '{"device_id":{"S":"vehicle-001"}}'
```

If there is no item, check the Lambda processor log group and Kinesis event source mapping. Verify that your producer used `--send`, the stream name was correct and the Lambda has DynamoDB write permissions.

## 6. Run the Glue ETL and crawler (extra cost)

This reads the raw zone, filters readings and writes Parquet to the curated bucket. The Glue crawler then registers a table.

```bash
python scripts/run_etl.py \
  --job REPLACE_WITH_GLUE_JOB_NAME \
  --crawler REPLACE_WITH_GLUE_CRAWLER_NAME \
  --region ap-south-1 --confirm-cost
```

Expected evidence:

- A successful Glue job run ID in the AWS Console.
- Parquet files under `s3://CURATED_BUCKET/telemetry/event_date=YYYY-MM-DD/`.
- A table in the `GlueDatabaseName` database after the crawler succeeds.

If you get a `NoSuchKey` for the Glue script, revisit step 3. If no raw data exists, revisit step 4. For repeated ETL runs, Glue bookmarks can avoid re-reading old input files, but duplicates across replays are still a design concern and should be measured.

## 7. Query with Athena (query bytes may be billed)

Verify the table name in **AWS Glue → Data Catalog → Tables**. It may differ from `telemetry` depending on the crawler output. Preview SQL without running it:

```bash
python scripts/query_athena.py \
  --database REPLACE_WITH_GLUE_DATABASE \
  --table telemetry \
  --results-bucket REPLACE_WITH_ARTIFACT_BUCKET
```

Execute when ready:

```bash
python scripts/query_athena.py \
  --database REPLACE_WITH_GLUE_DATABASE \
  --table telemetry \
  --results-bucket REPLACE_WITH_ARTIFACT_BUCKET --execute
```

The script runs a limited aggregate by device ID. Results are written to the **private artifacts bucket** under `athena-results/`.

## 8. Test the Cognito-protected API

The API is designed to reject anonymous requests. First test the authentication gate:

```bash
python scripts/smoke_test_api.py --api-url REPLACE_WITH_API_URL
```

Expected: `Unauthenticated GET: 401`.

To test an authenticated request, create a test Cognito user in **Amazon Cognito → User pools →** your pool, using the admin flow and a temporary password. Reset it to a permanent password and satisfy any configured challenges in the console. You can use `scripts/login_cognito.py` to sign in interactively (password is hidden) and, with `--show-token`, obtain a short-lived access token. **Treat the token as a secret; do not commit or screenshot it.**

```bash
python scripts/login_cognito.py --client-id REPLACE_WITH_CLIENT_ID --region ap-south-1 --show-token
```

Provide that token to the API check through the environment variable `DATA_LAKE_ACCESS_TOKEN` and rerun `smoke_test_api.py`. A valid user can read the latest record for a device; a nonexistent device returns HTTP 404. Device-level / tenant-level authorization is not implemented in the pilot.

## 9. Check logs and notifications

- CloudWatch Logs: inspect the processor function and the `/aws/kinesisfirehose/...` log group.
- CloudWatch Alarms: inspect the processor error alarm.
- SNS: manually create and confirm an **email subscription** for the `AlertTopicArn`. No email address is embedded in source code.
- Capture screenshots that show success/failure and redact AWS account numbers, ARNs and emails before public upload.

## 10. Clean up and avoid further charges

**Do not delete the stack until you've exported anything you need.** S3 buckets and the DynamoDB table are intentionally retained to reduce accidental data loss. They can keep accruing charges even after stack deletion.

```bash
aws cloudformation delete-stack --stack-name datasoftlake-dev --region ap-south-1
aws cloudformation wait stack-delete-complete --stack-name datasoftlake-dev --region ap-south-1
```

Then use the AWS Console to review and explicitly remove any retained **raw, curated and artifact S3 buckets** (including versions/delete markers), the **DynamoDB table**, CloudWatch log groups and any manually created resources if they are no longer needed. Verify in Billing/Cost Explorer and Resources/Tags views. **Do not automate bulk deletion of buckets containing real data.**

## 11. Evidence needed before calling this deployed

Use [AWS Evidence Template](../reports/AWS_EVIDENCE_TEMPLATE.md) to record the stack ID, date, exact region, sanitized output, Kinesis ingest, S3 object, Lambda/DynamoDB read, Glue and crawler run IDs, Athena query ID, Cognito 401/200 tests, alarms, cost estimate and cleanup status. Don't invent metrics or availability figures.
