# Architecture review and improvement summary

**Project:** Architecting and Deploying a Data Lake Automation Solution  
**Original context:** Datasoft Inc. capstone exercise, Advanced Certificate Program in Cloud Computing  
**Review type:** Source-to-design assessment and code starter; **not** an AWS production readiness certification

## Executive assessment

The original project establishes a useful service-level picture of an AWS data lake: ingest through Kinesis, persist in S3, transform with AWS Glue, expose operational data with DynamoDB/API Gateway and analyze it with Athena. The prior submission also contains a large set of screenshots showing IAM, CloudFormation, S3, Glue, CI/CD, security settings and multi-region configuration.

The main weakness is the gap between **describing or screenshotting a service** and **being able to reproduce, test and operate the complete solution from source control**. The report lists useful AWS CLI commands and code snippets, but it does not provide a verified integrated source package, a deployment/evidence matrix, automated offline tests, a current runtime baseline or consistent protections for public GitHub publication.

This repository addresses those gaps with executable Python components, CloudFormation/SAM, a private S3 + Kinesis + Firehose path, Cognito-secured API, Glue ETL, local test runner, GitHub Actions, operational documents and a saved copy of every original image. The stack remains **unverified in AWS** and intentionally does not pretend to implement every service pictured in the historical architecture.

## Specific findings and changes

| Priority | Finding in original materials | Improvement supplied | Remaining gap |
|---|---|---|---|
| High | Infrastructure steps scattered across screenshots and commands | One reviewable SAM/CloudFormation template for the pilot | Must deploy/validate in a real AWS account |
| High | Ingestion/ETL example code not provided as an end-to-end version-controlled repository | Python producer, Lambda consumer, Glue Spark job, Athena query helper | Real AWS integration and performance test needed |
| High | No explicit replay/idempotency rule for a per-device current state | Conditional DynamoDB write and partial Kinesis batch failures | Historical dedup and replay process still needed |
| High | API access requirements mention Cognito without a complete access boundary | JWT-authorized GET-only HTTP API | Per-tenant/device-level authorization is missing |
| High | Security checklist mixes enterprise controls with demo steps | Private S3, service roles, encryption, security review | Customer-managed KMS, governance grants and audits pending |
| Medium | Source reports use older AWS nomenclature and Python 3.8 examples | Python 3.12, OpenSearch naming, current CodeCommit availability | Revalidate managed-service versions before each release |
| Medium | Multi-region images could be mistaken for tested DR | Clear DR design and RPO/RTO evidence worksheet | No active-passive deployment or controlled failover performed |
| Medium | Screenshots are embedded in a large PDF | 91 original images extracted and categorized | Review source images for identifiers before public upload |
| Medium | No automated tests in the original submission | 16 local unit tests + GitHub Actions and Docker test runner | AWS service integration tests pending |
| Medium | Cloud costs not quantified | Cost-driver table, budget advice and explicit deploy confirmation | Actual AWS Pricing Calculator estimate needed |

## Architectural strengths of the revised pilot

1. **Traceability:** The architecture, source files, scripts, test coverage and original screenshots can be inspected independently.
2. **Operational separation:** Raw history stays in S3; DynamoDB stores a single latest-value view; Glue produces a curated analytical zone.
3. **Safer deployment:** Dev/test/prod parameter, change-set confirmation, S3 Block Public Access and explicit warnings about chargeable resources.
4. **Security by default:** Anonymous API requests are rejected. The read path has no write permissions to DynamoDB.
5. **Reproducibility:** Local unit tests and containerized tests use synthetic fixtures, not live AWS data.

## Important production blockers

- The complete stack must pass **`sam validate --lint`**, deployment and end-to-end smoke testing in an AWS sandbox. CloudFormation source correctness and IAM permissions cannot be proven by offline YAML parsing alone.
- Governance: implement Lake Formation policy, classification, data ownership and privacy decisions.
- Authorization: add ownership/tenant checks before exposing any real device data.
- Batch: add a bad-record quarantine, schema versioning, run-to-run dedup or transactional table format, operational monitoring and retry policy.
- Disaster recovery: test actual S3 replication, DynamoDB Global Tables, secondary endpoints and measurable recovery objectives.
- CI/CD: provision AWS CodePipeline / CodeBuild resources, deployment roles and approval gates if required for production deployment.
- Security: inspect original screenshots and PDFs for account identifiers before public distribution, add secret scanning and evaluate customer-managed KMS keys.
- FinOps: prepare a time-limited cost estimate, cost allocation tags, alert thresholds and an approved cleanup runbook.

## Recommended staged implementation

**Phase 1 - Local quality:** run unit tests, verify project structure, inspect screenshots and test the Docker runner. No AWS costs.

**Phase 2 - AWS sandbox:** deploy one region with synthetic records, verify raw S3 and DynamoDB, run Glue and Athena, test Cognito API authentication; record output/alarms/costs.

**Phase 3 - Governance and release:** add Lake Formation and tenant authorization, CodePipeline/change-set approval, integration tests and automated quality checks.

**Phase 4 - Regional resilience:** implement a secondary region, cross-region replication, recovery capacity and controlled failover drills; record RPO and RTO.

## Evidence required for portfolio claims

Only claim an AWS resource was *deployed*, a pipeline *executed*, an alarm *delivered*, or a recovery exercise *passed* after obtaining a dated stack/resource ID, sanitized screenshot, relevant CloudWatch/event log and actual outcome. Until then, describe the work as an **architected and implemented reference solution with local code validation**.

## Source basis

- `docs/source/capstone_assignment.pdf` (8 pages): business problem, target services, ingest/decode/transform/analyze/consume deliverables and original architecture.
- `docs/source/original_project_report.pdf` (32 pages): prior setup instructions, AWS console screenshots, infrastructure/service examples and original submission.
- Current AWS documentation for Lambda runtimes, Kinesis batch failure responses, Data Firehose, CodeCommit and OpenSearch (linked in `docs/SERVICE_COVERAGE.md`).
