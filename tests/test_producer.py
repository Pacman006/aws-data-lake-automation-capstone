import json
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from produce_telemetry import generate_events, send_events


class ProducerTests(unittest.TestCase):
    def test_count_and_shape(self):
        rows = list(generate_events(3, 'car-01'))
        self.assertEqual(len(rows), 3)
        self.assertEqual({row['device_id'] for row in rows}, {'car-01'})

    def test_stream_payload_has_newline_for_firehose(self):
        client = Mock()
        row = list(generate_events(1, 'car-01'))[0]
        self.assertEqual(send_events(client, 'demo-stream', [row]), 1)
        sent = client.put_record.call_args.kwargs
        self.assertEqual(sent['PartitionKey'], 'car-01')
        self.assertTrue(sent['Data'].endswith(b'\n'))
        self.assertEqual(json.loads(sent['Data']), row)


if __name__ == '__main__':
    unittest.main()
