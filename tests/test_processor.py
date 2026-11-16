import base64
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

from botocore.exceptions import ClientError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from telemetry_processor.app import process_batch, store_latest


def make_record(payload, seq='100'):
    body = json.dumps(payload) if isinstance(payload, dict) else payload
    return {'kinesis': {'sequenceNumber': seq, 'data': base64.b64encode(body.encode()).decode()}}


VALID = {
    'event_id': 'evt-01', 'device_id': 'car-01', 'event_time': '2026-11-16T11:00:00Z',
    'speed_kmh': 34.5, 'fuel_percent': 69, 'diagnostic_codes': [],
}


class ProcessorTests(unittest.TestCase):
    def test_saves_valid_record(self):
        table = Mock()
        result = process_batch({'Records': [make_record(VALID)]}, table)
        self.assertEqual(result, {'batchItemFailures': []})
        table.put_item.assert_called_once()
        args = table.put_item.call_args.kwargs
        self.assertIn('event_time < :new_time', args['ConditionExpression'])
        self.assertEqual(args['Item']['device_id'], 'car-01')

    def test_invalid_json_is_discarded(self):
        table = Mock()
        self.assertEqual(process_batch({'Records': [make_record('{invalid')]}, table), {'batchItemFailures': []})
        table.put_item.assert_not_called()

    def test_transient_database_failure_reports_sequence(self):
        table = Mock()
        table.put_item.side_effect = RuntimeError('DynamoDB unavailable')
        result = process_batch({'Records': [make_record(VALID, '556')]}, table)
        self.assertEqual(result, {'batchItemFailures': [{'itemIdentifier': '556'}]})

    def test_replayed_record_is_not_an_error(self):
        table = Mock()
        table.put_item.side_effect = ClientError(
            {'Error': {'Code': 'ConditionalCheckFailedException', 'Message': 'Old reading'}},
            'PutItem',
        )
        self.assertFalse(store_latest(table, VALID))

    def test_unexpected_dynamodb_error_rethrows(self):
        table = Mock()
        table.put_item.side_effect = ClientError(
            {'Error': {'Code': 'ProvisionedThroughputExceededException', 'Message': 'Busy'}},
            'PutItem',
        )
        with self.assertRaises(ClientError):
            store_latest(table, VALID)


if __name__ == '__main__':
    unittest.main()
