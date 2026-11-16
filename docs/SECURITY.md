# Security and data governance review

## Baseline controls included in the source

| Control | Implementation | Additional work before production |
|---|---|---|
| Private data | S3 Block Public Access + BucketOwnerEnforced | Account-level public access guardrails and data classification |
| Encryption at rest | S3 SSE-S3, Kinesis AWS-managed KMS key, DynamoDB SSE | Customer-managed KMS keys if policy mandates them; key rotation and access review |
| Authentication | Cognito user pool, user-created accounts only | MFA, external identity federation, user lifecycle |
| API authorization | API Gateway HTTP JWT authorizer | **Per-tenant / device ownership authorization** (not implemented) |
| IAM | Dedicated Lambda, Firehose and Glue execution roles | Validate least privilege with IAM Access Analyzer and org policies |
| Data retention | S3 versioning and retained data resources | Lifecycle rules, legal holds, deletion requests, retention schedule |
| Audit / monitoring | Lambda tracing, CloudWatch alarm, AWS service logs | CloudTrail, Security Hub, Config, centralized audit archive |
| Code integrity | Unit tests, GitHub Actions, change-set confirmation | Pull request protection, secret scanning and dependency scanning |

## Important findings

**A Cognito JWT identifies an authenticated API caller; it does not prove that the caller may read a particular vehicle's data.** The demo endpoint is suitable only for synthetic data in a controlled sandbox. Do not use with real customers until tenant ownership is checked before DynamoDB reads.

The original screenshots include AWS Management Console, terminals and Git credentials flows. They might show account IDs, URLs, hostnames or names that should not be published. **Review `docs/images/original/` and the source PDFs before making this repository public.** If necessary, retain full originals privately and publish sanitized copies with a note describing the edits.

Do not place credentials in Git, CloudFormation parameters, query strings, screenshots, `.env` files or shell history. Prefer AWS IAM Identity Center or temporary role credentials. The login helper prompts for a password without echoing it; if you use `--show-token`, the token is sensitive and should not be saved or photographed.

## Encryption and KMS

The assignment mentions AWS KMS, but the core pilot deliberately avoids creating customer-managed keys with an unreviewed key policy. Kinesis uses AWS-managed KMS encryption, while S3 and DynamoDB use their configured service-side encryption. For production workloads requiring customer-managed KMS keys, design policies for Firehose, Lambda, Glue, Athena and cross-region replication before switching to SSE-KMS; then test key access failures and rotation.

## Lake Formation

The earlier report mentions Lake Formation. The pilot creates a Glue Data Catalog database but **does not register S3 data locations in Lake Formation or grant data permissions**. For organization-wide use, define separate producer, analyst, admin and data steward roles, register data locations, define data grants and audit query access. Do not present Glue's database alone as a Lake Formation governance implementation.

## Recommended pre-deployment review

1. Identify whether the data includes location trails, personal identifiers or confidential business information.
2. Decide retention period, acceptable uses and users allowed to view each dataset.
3. Review CloudFormation IAM statements and the selected AWS region.
4. Enable account-level logging and alert destinations and validate the alert subscription.
5. Create an AWS budget alarm and record a rollback / cleanup plan.
6. Run all tests and get a peer review before deploying into any shared account.
