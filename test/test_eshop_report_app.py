import json
import unittest

import eshop_report_app


class TestEndpoint(unittest.TestCase):

    def setUp(self):
        self.app = eshop_report_app.app.test_client()
        self.app.testing = True

    def test_request_to_root_returns_helpful_msg(self):
        result = self.app.get('/')
        self.assertEqual(eshop_report_app.LANDING_MSG.encode(), result.data)

    def test_missing_param_returns_helpful_msg(self):
        request_str = eshop_report_app.ENDPOINT_PATH + '?y=2019&d=01'
        result = self.app.get(request_str)
        self.assertEqual(eshop_report_app.MISSING_PARAM_ERR_MSG.encode(), result.data)

    def test_non_existent_date_returns_helpful_msg(self):
        request_str = eshop_report_app.ENDPOINT_PATH + '?y=2019&m=2&d=30'
        result = self.app.get(request_str)
        self.assertEqual(eshop_report_app.DATE_PARSE_ERR_MSG.encode(), result.data)

    def test_non_numeric_date_returns_helpful_msg(self):
        request_str = eshop_report_app.ENDPOINT_PATH + '?y=foo&m=bar&d=baz'
        result = self.app.get(request_str)
        self.assertEqual(eshop_report_app.DATE_PARSE_ERR_MSG.encode(), result.data)

    def test_all_fields_present_for_correct_date(self):
        request_str = eshop_report_app.ENDPOINT_PATH + '?y=2019&m=8&d=1'
        result = self.app.get(request_str)

        expected_result_keys = {'customers', 'total_discount_amount', 'items',
                                'order_total_avg', 'discount_rate_avg', 'commissions'}
        actual_result_keys = set(json.loads(result.data).keys())

        self.assertEqual(expected_result_keys, actual_result_keys)
