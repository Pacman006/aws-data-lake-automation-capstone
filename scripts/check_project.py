#!/usr/bin/env python3
"""Offline project checks. Does not require AWS credentials or create resources."""
import ast
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    'cloudformation/template.yaml', 'src/shared/schema.py', 'src/telemetry_processor/app.py',
    'src/query_api/app.py', 'glue/transform_telemetry.py', 'README.md',
    'docs/source/original_project_report.pdf', 'docs/source/capstone_assignment.pdf',
    'docs/images/image_inventory.json', '.github/workflows/ci.yml',
]


def main():
    for name in REQUIRED:
        if not (ROOT / name).is_file():
            print('MISSING:', name)
            return 1
    for file in [*ROOT.glob('src/**/*.py'), *ROOT.glob('scripts/*.py'), *ROOT.glob('tests/*.py'), *ROOT.glob('glue/*.py')]:
        ast.parse(file.read_text(encoding='utf-8'), filename=str(file))
    inventory = json.loads((ROOT / 'docs/images/image_inventory.json').read_text())
    if not inventory or any(not (ROOT / item['file']).is_file() for item in inventory):
        print('Image gallery incomplete')
        return 1
    try:
        import yaml
    except ImportError:
        print('PyYAML missing: python -m pip install -r requirements-dev.txt')
        return 1

    class Loader(yaml.SafeLoader):
        pass
    for tag in ('Ref', 'Sub', 'GetAtt', 'Join', 'If', 'Equals', 'GetAZs', 'Select', 'FindInMap'):
        Loader.add_constructor('!' + tag, lambda loader, node, name=tag: {
            'Fn::' + name if name != 'Ref' else 'Ref': (
                loader.construct_scalar(node) if isinstance(node, yaml.ScalarNode) else
                loader.construct_sequence(node) if isinstance(node, yaml.SequenceNode) else
                loader.construct_mapping(node)
            )
        })
    template = yaml.load((ROOT / 'cloudformation/template.yaml').read_text(), Loader=Loader)
    resources = template['Resources']
    expected = ['RawBucket', 'TelemetryStream', 'RawDelivery', 'Processor', 'ReadLatest', 'UserPool', 'HttpApi', 'TransformJob', 'CuratedCrawler']
    assert all(name in resources for name in expected)
    assert resources['ReadRoute']['Properties']['AuthorizationType'] == 'JWT'
    assert len(inventory) >= 30
    print(f"Offline project checks passed: {len(resources)} CloudFormation resources, {len(inventory)} source images.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
