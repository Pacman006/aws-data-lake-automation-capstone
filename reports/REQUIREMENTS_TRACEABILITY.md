# Requirement-to-implementation traceability

This table maps the two supplied PDFs to the source in this repository. **Implemented in source** means the file exists and local logic can be tested; it does **not** mean a live AWS environment has been exercised.

| Original requirement | Source / page | Repository deliverable | Assessment |
|---|---|---|---|
| Consolidate decentralized data with a dependable lake | Assignment p.3; report p.1 | `cloudformation/template.yaml`, S3 raw and curated zones | Pilot design and source provided |
| Ingest connected-vehicle records continuously | Assignment p.6 | Kinesis stream, Firehose delivery, `scripts/produce_telemetry.py` | Implemented in source |
| Decode proprietary binary vehicle messages | Assignment p.6 | Typed JSON event schema in `src/shared/schema.py` | **Not implemented:** actual binary format/specification was not supplied |
| Preserve original records | Assignment pp.5-6 | Firehose archives newline-delimited records to raw S3 | Implemented in source |
| Transform to queryable data | Assignment pp.5-6; report pp.9-12 | `glue/transform_telemetry.py`, Parquet in curated S3 | Implemented in source; no AWS run evidence |
| Data quality and validation | Assignment p.3 | Python schema validation, Glue filtering and unit tests | Pilot-level checks |
| Query data using Athena | Assignment pp.5-6; report pp.11, 15-16 | Glue crawler/database and `scripts/query_athena.py` | Implemented in source; no query run evidence |
| Metadata catalog | Report p.1 | AWS Glue Data Catalog database/crawler | Partial; Lake Formation permissions absent |
| Current data served to apps | Assignment pp.5-6 | DynamoDB latest-per-device table + API Gateway/Lambda | Partial; missing full data-package/cart API |
| Authentication for console / APIs | Assignment pp.4-5 | Cognito + JWT authorizer on read-only HTTP API | Partial; no console UI or tenant authorization |
| Full-text dataset search | Assignment pp.4-5 | OpenSearch architecture discussion | Not implemented; requires search/index design |
| Dashboard / visualization | Assignment pp.4-5 | Source architecture and documentation | Not implemented; QuickSight not provisioned |
| Static console delivery | Assignment p.4 | Original diagrams retained | Not implemented; CloudFront not provisioned |
| End-to-end developer CI/CD | Assignment p.6; report pp.14, 26-32 | GitHub Actions CI and CodeBuild starter | Partial; AWS CodePipeline not provisioned |
| Security and encryption | Assignment pp.6-7; report pp.16-19 | Private S3, AWS-managed/SSE encryption, IAM roles, Cognito | Partial; KMS CMKs, central audit, Lake Formation grants pending |
| Monitoring / alert notification | Assignment pp.4-6 | CloudWatch logs/error alarm and SNS topic | Partial; subscriptions and more alarms pending |
| S3 cross-region replication | Report pp.20-21 | DR/cost/runbook documentation | Not implemented |
| DynamoDB Global Tables | Report pp.22-23 | DR/cost/runbook documentation | Not implemented |
| Detailed project steps and screenshots | Assignment p.8; report throughout | Markdown guides, PDF review, both originals + 91 extracted images | Provided; verify privacy before upload |

## Key observation

The source brief mentions a **proprietary bit-level vehicle decoder**, but provides no binary message specification, test vectors or expected decoded fields. Writing a pretend binary decoder would be misleading. This pilot uses an explicit synthetic JSON contract instead. If the encoding specification becomes available, add a decoder module with documented tests and sample binaries.

The original architecture also includes a data lake console and data-package/cart workflows. The current API is intentionally much narrower: one read-only latest-reading endpoint protected by Cognito. A complete portal would require a separate access model, inventory/catalog API, front-end, user flows and security testing.
