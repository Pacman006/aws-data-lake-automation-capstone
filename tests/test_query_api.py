import json
import sys
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from query_api.app import read_device


class QueryApiTests(unittest.TestCase):
    def test_found(self):
        table = Mock()
        table.get_item.return_value = {'Item': {'device_id': 'car-1', 'speed_kmh': Decimal('25.4')}}
        answer = read_device({'pathParameters': {'device_id': 'car-1'}}, table)
        self.assertEqual(answer['statusCode'], 200)
        self.assertEqual(json.loads(answer['body'])['speed_kmh'], 25.4)
        self.assertEqual(answer['headers']['cache-control'], 'no-store')

    def test_missing(self):
        table = Mock()
        table.get_item.return_value = {}
        self.assertEqual(read_device({'pathParameters': {'device_id': 'car-2'}}, table)['statusCode'], 404)

    def test_bad_path(self):
        table = Mock()
        self.assertEqual(read_device({'pathParameters': {'device_id': '../x'}}, table)['statusCode'], 400)
        table.get_item.assert_not_called()


if __name__ == '__main__':
    unittest.main()
