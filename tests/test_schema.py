import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from shared.schema import InvalidTelemetry, validate_record


class SchemaTests(unittest.TestCase):
    def setUp(self):
        self.event = {
            'event_id': 'sample-001', 'device_id': 'car-01',
            'event_time': '2026-11-16T09:00:00+05:30',
            'speed_kmh': 75, 'fuel_percent': 42.5,
            'diagnostic_codes': [],
        }

    def test_valid_record_converts_time_to_utc(self):
        data = validate_record(self.event)
        self.assertEqual(data['event_time'], '2026-11-16T03:30:00Z')
        self.assertEqual(data['speed_kmh'], 75.0)

    def test_reject_missing_timezone(self):
        self.event['event_time'] = '2026-11-16T09:00:00'
        with self.assertRaises(InvalidTelemetry):
            validate_record(self.event)

    def test_reject_negative_speed(self):
        self.event['speed_kmh'] = -1
        with self.assertRaises(InvalidTelemetry):
            validate_record(self.event)

    def test_reject_invalid_device_id(self):
        self.event['device_id'] = '../../private'
        with self.assertRaises(InvalidTelemetry):
            validate_record(self.event)

    def test_reject_boolean_metric(self):
        self.event['fuel_percent'] = True
        with self.assertRaises(InvalidTelemetry):
            validate_record(self.event)

    def test_reject_too_many_codes(self):
        self.event['diagnostic_codes'] = ['X'] * 21
        with self.assertRaises(InvalidTelemetry):
            validate_record(self.event)


if __name__ == '__main__':
    unittest.main()
