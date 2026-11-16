# Local verification summary

**Scope:** Python unit tests and project structure checks in a sandbox environment, not live AWS infrastructure.

| Check | Result |
|---|---|
| Unit tests | 16 passed |
| Python parsing | Passed for local source, scripts, tests and Glue program |
| CloudFormation template structure | Passed offline YAML / resource checks (32 resources) |
| Original screenshot extraction | 91 embedded images retained |
| Docker build/run | Not tested in the authoring environment |
| AWS SAM lint | Not tested in the authoring environment |
| AWS deployment | Not performed |
| Cloud service integration | Not performed |
| Regional failover | Not performed |

Re-run tests on your machine or GitHub Actions before making claims about current code. Use `python scripts/generate_local_report.py` to create a fresh timestamped report after a local run. A passing local test does **not** guarantee CloudFormation stack creation or production readiness.
