# Availability, disaster recovery and cost considerations

## Recovery strategy

The earlier project document shows S3 cross-region replication and DynamoDB Global Tables, but those screenshots are **not evidence of a tested regional recovery for the code in this repository**. The provided SAM template deploys to **one AWS region**.

Before claiming multi-region resilience:

1. Decide business RPO (maximum tolerable data loss) and RTO (maximum restoration time) in writing.
2. Create a second-region destination bucket with versioning, the right security policies and replication IAM role.
3. Configure S3 cross-region replication for eligible data, including existing objects if required; verify object availability in the destination.
4. Evaluate DynamoDB Global Tables for the latest-reading view, including conflict resolution and replication cost.
5. Deploy the producer ingress, Lambda processor, API, Cognito/identity strategy and Glue resources in the secondary region.
6. Plan client traffic failover, application secrets, DNS, state repair, backfill and authorization policies.
7. Test an actual regional failure scenario and record RPO/RTO rather than assigning estimated improvements.

**Important:** Replicating S3 raw data is not sufficient to fail over the read API; DynamoDB data, Cognito configuration and compute endpoints must also be available.

## Cost drivers

| Service | Why charges can rise | Pilot control |
|---|---|---|
| Kinesis Data Streams | Provisioned shard running continuously | Use one shard and delete stack when testing ends |
| Firehose | Records ingested and delivered | Send tiny sample volumes |
| S3 | Storage, requests, versions, cross-region transfer | Use synthetic data and clean retained versions intentionally |
| Lambda | Invocation and duration | Small records and bounded tests |
| DynamoDB | Requests, storage, PITR and cross-region replication | Small item count, short pilot lifetime |
| Glue | Spark worker execution and crawler duration | Run manually, use minimal worker count and bound data volume |
| Athena | Data scanned by queries | Query Parquet and restrict columns/partitions |
| CloudWatch | Logs, metrics, retention | Short retention where suitable, avoid verbose personal data logs |
| OpenSearch / QuickSight / CloudFront | Not in the core stack | Do not create until justified and budgeted |

There is deliberately no hard-coded monthly price or claimed cost saving. Use the current [AWS Pricing Calculator](https://calculator.aws/) with actual region, workload size and intended usage, and record the quote date.

## Teardown

The script-based deployment requires manual cleanup after deleting the CloudFormation stack because data buckets and the DynamoDB table use `Retain`. See the [AWS Deployment Guide](AWS_DEPLOYMENT.md) and verify Billing/Cost Explorer afterwards.
