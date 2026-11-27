import unittest

import pandas as pd

from config import FEATURES_ALLOWED
from src.data_loading import validate_features


class FeatureAllowlistTests(unittest.TestCase):
    def test_allowed_columns_pass(self):
        frame = pd.DataFrame({
            "FlightDate": ["2024-02-01"],
            "Origin": ["ATL"],
            "CRSDepTime": [1200],
            "Distance": [500],
        })
        self.assertIs(validate_features(frame), frame)

    def test_leakage_columns_fail(self):
        forbidden = [
            "AirTime",
            "Cancelled",
            "CancellationCode",
            "Tail_Number",
            "ArrDelay",
        ]
        for column in forbidden:
            with self.subTest(column=column):
                frame = pd.DataFrame({column: [1]})
                with self.assertRaises(ValueError):
                    validate_features(frame)

    def test_allowlist_is_not_empty_and_has_no_targets(self):
        forbidden_targets = {
            "AirTime",
            "ArrDelay",
            "ArrDelayMinutes",
            "ArrDel15",
            "CarrierDelay",
            "WeatherDelay",
            "NASDelay",
            "SecurityDelay",
            "LateAircraftDelay",
            "Cancelled",
            "CancellationCode",
            "Tail_Number",
        }
        self.assertTrue(FEATURES_ALLOWED)
        self.assertTrue(FEATURES_ALLOWED.isdisjoint(forbidden_targets))


if __name__ == "__main__":
    unittest.main()
