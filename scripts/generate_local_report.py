#!/usr/bin/env python3
"""Run offline checks and write a truthful, timestamped validation report."""
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / 'reports'


def run(command):
    try:
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=120)
        return {'status': 'PASS' if result.returncode == 0 else 'FAIL',
                'exit_code': result.returncode, 'output': (result.stdout + result.stderr)[-5000:]}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {'status': 'NOT_RUN', 'exit_code': None, 'output': str(exc)}


def main():
    results = {
        'generated_at_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'python': platform.python_version(),
        'scope': 'Offline unit tests and source/template checks. No AWS services were deployed.',
        'unit_tests': run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v']),
        'project_check': run([sys.executable, 'scripts/check_project.py']),
        'aws_deployment': 'NOT_TESTED',
        'docker_build': 'NOT_TESTED',
        'glue_etl_in_aws': 'NOT_TESTED',
        'regional_recovery': 'NOT_TESTED',
    }
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / 'local_validation_latest.json').write_text(json.dumps(results, indent=2) + '\n')
    lines = [
        '# Local validation report', '',
        f"Generated (UTC): {results['generated_at_utc']}", '',
        f"Python: {results['python']}", '',
        '> This report checks local code only. It is not evidence of successful AWS deployment.', '',
    ]
    for key in ['unit_tests', 'project_check']:
        item = results[key]
        lines.extend([f"## {key.replace('_', ' ').title()}: {item['status']}", '', '```text', item['output'].strip() or '(no output)', '```', ''])
    lines.extend(['## Checks requiring AWS or Docker', '',
                  '- AWS deployment: NOT TESTED', '- Docker: NOT TESTED',
                  '- Glue ETL in AWS: NOT TESTED', '- Regional recovery: NOT TESTED', ''])
    (REPORTS / 'local_validation_latest.md').write_text('\n'.join(lines), encoding='utf-8')
    print('Reports saved in reports/local_validation_latest.{json,md}')
    return 0 if all(results[k]['status'] == 'PASS' for k in ('unit_tests', 'project_check')) else 1


if __name__ == '__main__':
    raise SystemExit(main())
