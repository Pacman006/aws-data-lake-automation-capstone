# AWS service coverage: implemented versus planned

This matrix is intended to prevent a GitHub reader from confusing the **original capstone's target architecture** with the **code that can be deployed from this repository**.

| AWS service / feature | In the original material | In this repository | Status |
|---|---|---|---|
| AWS CloudFormation | Yes | `cloudformation/template.yaml` (AWS SAM transform) | **Implemented in source, not AWS-tested** |
| Kinesis Data Streams | Yes | Stream, Python producer, Lambda event source mapping | **Implemented in source** |
| Amazon Data Firehose | Yes | Reads Kinesis and archives raw JSONL to S3 | **Implemented in source** |
| Amazon S3 | Yes | Private raw, curated and artifacts buckets | **Implemented in source** |
| AWS Lambda | Yes | Stream processor and read API functions | **Implemented in source** |
| Amazon DynamoDB | Yes | Latest-per-device table and conditional writes | **Implemented in source** |
| API Gateway | Yes | JWT-protected `GET /devices/{device_id}/latest` | **Implemented in source** |
| Amazon Cognito | Yes | User pool and app client, admin-created users | **Implemented in source** |
| AWS Glue ETL | Yes | Glue Spark job and catalog crawler | **Implemented in source** |
| Amazon Athena | Yes | Glue database, read-only query runner | **Implemented in source** |
| AWS CloudWatch | Yes | Log groups and Lambda error alarm | **Partly implemented** |
| Amazon SNS | Yes | Alarm topic; subscription must be configured manually | **Partly implemented** |
| AWS IAM | Yes | Scoped processor, query, Firehose and Glue execution roles | **Implemented in source; review before deployment** |
| AWS KMS | Yes | Kinesis uses AWS-managed key `alias/aws/kinesis`; S3 SSE-S3, DynamoDB encrypted by AWS | **Customer-managed KMS not implemented** |
| AWS Lake Formation | Project report | Catalog exists, but no LF permissions/grants or LF data locations configured | **Follow-up** |
| CloudFront + website | Yes, in original architecture | Original image retained; no hosted console | **Not implemented** |
| Amazon OpenSearch Service | Called Elasticsearch Service in older brief | No domain, serverless collection or search indexing function | **Not implemented** |
| Amazon QuickSight | Yes | Athena data source design described; no dashboard | **Not implemented** |
| AWS CodeBuild | Yes | `buildspec.yml` for tests | **Starter only** |
| AWS CodePipeline | Yes | CI/CD guide; no AWS-managed pipeline resource | **Not implemented** |
| AWS CodeCommit | Yes, in older screenshots | GitHub-first; CodeCommit optional source alternative | **Not implemented** |
| GitHub Actions | Not in original report | `.github/workflows/ci.yml` | **Implemented in source** |
| S3 cross-region replication | Yes, screenshots | Operational plan only; no replication rule | **Not implemented** |
| DynamoDB Global Tables | Yes, screenshots | DynamoDB single-region table | **Not implemented** |
| Data quality | Requested | Schema checks in Lambda; basic Glue filtering | **Pilot level** |
| Full DR test, RPO/RTO | Requested | Runbook and evidence worksheet | **Not performed** |

## Modern AWS naming and updates

- **Amazon Elasticsearch Service** was renamed **Amazon OpenSearch Service** in 2021. The older name is preserved only when referring to screenshots in the original report.
- **AWS CodeCommit returned to general availability and new-customer access in November 2025**. GitHub remains the publication target for this project; CodeCommit can still be considered for an internal AWS source repository.
- The older sample command in the project report targets the **Python 3.8 Lambda runtime**. This code uses **Python 3.12** to avoid that obsolete runtime.
- The original brief mentions an admin IAM role for initial setup. The project deploy scripts require an authorized identity capable of creating IAM roles, but should be run with a dedicated deployment role under an AWS budget, not permanent admin user keys.

## Sources

- [AWS Lambda runtimes](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html)
- [CodeCommit documentation history](https://docs.aws.amazon.com/codecommit/latest/userguide/history.html)
- [AWS CodeCommit general availability announcement](https://aws.amazon.com/blogs/devops/aws-codecommit-returns-to-general-availability/)
- [Amazon OpenSearch Service FAQs](https://aws.amazon.com/opensearch-service/faqs/)
- [Lambda Kinesis partial-batch responses](https://docs.aws.amazon.com/lambda/latest/dg/services-kinesis-batchfailurereporting.html)
