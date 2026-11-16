# Release and review checklist

Before publishing to GitHub:

- [ ] Inspect both original PDFs and all extracted screenshots for sensitive account information.
- [ ] Confirm the public repository contains no AWS credentials, private keys, tokens or real customer data.
- [ ] Run `python -m unittest discover -s tests -v`.
- [ ] Run `python scripts/check_project.py`.
- [ ] Run `python scripts/generate_local_report.py` and review the generated status.
- [ ] Review the CloudFormation template's IAM permissions and data retention behavior.
- [ ] Confirm the README clearly marks AWS deployment as **not verified**.
- [ ] Create/push a dedicated repository to `Pacman006/aws-data-lake-automation-capstone`.
- [ ] Open GitHub Actions; do not claim success until all desired CI jobs pass.

Before AWS pilot deployment:

- [ ] AWS Budget created and alert recipient confirmed.
- [ ] IAM deployment principal uses temporary credentials and has authorized permissions.
- [ ] Intended region, environment and stack name confirmed.
- [ ] CloudFormation change set reviewed, especially IAM roles and S3 retention.
- [ ] AWS SAM validation passed locally / in GitHub Actions.
- [ ] Run first tests with only synthetic telemetry.
- [ ] Save sanitized deployment outputs and test records in `AWS_EVIDENCE_TEMPLATE.md`.
- [ ] Clean up chargeable resources and verify billing afterwards.

Before saying the solution is production ready:

- [ ] Per-tenant authorization, privacy review and Lake Formation permissions completed.
- [ ] Data quality, replay, monitoring and alert thresholds verified.
- [ ] CI/CD production approval and rollback procedure exercised.
- [ ] Multi-region recovery design implemented, drilled and RPO/RTO recorded.
- [ ] SRE ownership, incident response and operational cost model approved.
