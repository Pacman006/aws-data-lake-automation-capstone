# Local testing, scripts and Docker

## Purpose

The local environment checks source-code behavior without AWS credentials. Unit tests mock DynamoDB and Kinesis APIs; they do **not** claim to test actual managed-service availability. The Docker image exists only to run the tests consistently on another computer.

## Python environment

From the project root:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/macOS:
# source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python scripts/check_project.py
python scripts/generate_local_report.py
```

Generated reports: `reports/local_validation_latest.md` and `reports/local_validation_latest.json`. These are intentionally ignored by Git because they describe the machine on which they were run. A stable overview lives in [Local Verification Summary](../reports/LOCAL_VERIFICATION_SUMMARY.md).

## Docker container: build, run and remove

**Prerequisite:** Docker Desktop (Windows) or Docker Engine (Linux/macOS) must be installed and running.

```bash
# Build the local test image
docker build -t datasoft-data-lake-tests:local .

# Execute the tests in a temporary container
docker run --rm datasoft-data-lake-tests:local

# Or use Docker Compose
docker compose run --build --rm tests

# Remove the image when finished
docker image rm datasoft-data-lake-tests:local
```

There is no exposed HTTP port: this Dockerfile doesn't run a website. The deployed API is an API Gateway endpoint and Lambda function. Docker testing isn't proof that the AWS resources have been provisioned.

## Complete script inventory

| Script | What it does | AWS calls by default? |
|---|---|---|
| `scripts/preflight.py` | Checks tools and optional AWS identity | Only with `--aws` |
| `scripts/produce_telemetry.py` | Generates sample data | No; only sends with `--send` |
| `scripts/check_project.py` | Checks files, Python syntax, image inventory and SAM shape | No |
| `scripts/generate_local_report.py` | Runs local checks and writes timestamped reports | No |
| `scripts/deploy.sh` | SAM stack build/deploy after explicit confirmation | **Yes** |
| `scripts/deploy.ps1` | Windows PowerShell deployment equivalent | **Yes** |
| `scripts/upload_glue_script.py` | Uploads Spark ETL source to S3 | **Yes** |
| `scripts/run_etl.py` | Starts Glue ETL + optional crawler with cost confirmation | **Yes** |
| `scripts/query_athena.py` | Previews SQL or executes when `--execute` is supplied | Only with `--execute` |
| `scripts/login_cognito.py` | Signs in a test user to Cognito | **Yes** |
| `scripts/smoke_test_api.py` | Tests auth rejection, optionally valid token access | **Yes**, only to given URL |
| `glue/transform_telemetry.py` | Glue Spark job, runs inside AWS Glue | N/A |
| `src/telemetry_processor/app.py` | Kinesis Lambda consumer | N/A |
| `src/query_api/app.py` | Cognito-protected read API Lambda | N/A |
| `scripts/extract_original_images.py` | Re-extracts embedded images from the two PDFs | No |

## What the unit tests cover

- Good telemetry and UTC timestamp normalization.
- Rejection of invalid device IDs, timestamps, numbers and diagnostic codes.
- DynamoDB conditional writes and replay protection.
- Kinesis partial-batch failure response on transient store errors.
- Rejection of malformed JSON without infinite retries.
- API 200 / 400 / 404 response handling and Decimal serialization.
- Producer newline formatting required for Firehose JSONL archival.

## Local limitations

No unit test here simulates AWS network, IAM service authorization, Glue Spark runtime, Athena billing behavior, actual Firehose buffering, Cognito token verification, multi-region recovery or SNS delivery. Those need the deployment guide and signed-off AWS evidence.
