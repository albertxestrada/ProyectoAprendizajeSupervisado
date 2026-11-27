import unittest

import pandas as pd

from src.feature_engineering import compute_bearing
from src.preprocessing import (
    build_classification_label,
    convert_crs_to_utc,
    split_temporal,
)


class P3PreprocessingTests(unittest.TestCase):
    def test_2400_uses_next_day_in_utc(self):
        frame = pd.DataFrame({
            "FlightDate": ["2024-07-01"],
            "CRSDepTime": [2400],
            "Origin": ["ATL"],
        })
        result = convert_crs_to_utc(frame)
        expected = pd.Timestamp("2024-07-02T04:00:00Z")
        self.assertEqual(result.loc[0, "dep_datetime_utc"], expected)
        self.assertEqual(
            result.loc[0, "prediction_time_utc"],
            expected - pd.Timedelta(hours=4),
        )
        self.assertEqual(
            result.loc[0, "pred_datetime_utc"],
            result.loc[0, "prediction_time_utc"],
        )

    def test_delay_threshold_is_inclusive(self):
        frame = pd.DataFrame({
            "Cancelled": [0],
            "CancellationCode": [None],
            "ArrDelay": [15],
            "CarrierDelay": [0],
            "WeatherDelay": [0],
            "NASDelay": [15],
            "SecurityDelay": [0],
            "LateAircraftDelay": [0],
        })
        result = build_classification_label(frame)
        self.assertEqual(result.loc[0, "delay_label"], "Delay_NAS")

    def test_missing_cause_does_not_invent_security(self):
        frame = pd.DataFrame({
            "Cancelled": [0],
            "CancellationCode": [None],
            "ArrDelay": [20],
            "CarrierDelay": [0],
            "WeatherDelay": [0],
            "NASDelay": [0],
            "SecurityDelay": [0],
            "LateAircraftDelay": [0],
        })
        result = build_classification_label(frame)
        self.assertTrue(pd.isna(result.loc[0, "delay_label"]))
        self.assertTrue(result.loc[0, "label_quarantine"])
        self.assertEqual(result.loc[0, "quarantine_reason"], "missing_delay_cause")

    def test_cancelled_flights_are_quarantined(self):
        frame = pd.DataFrame({
            "Cancelled": [1],
            "CancellationCode": ["A"],
            "ArrDelay": [None],
            "CarrierDelay": [0],
            "WeatherDelay": [0],
            "NASDelay": [0],
            "SecurityDelay": [0],
            "LateAircraftDelay": [0],
        })
        result = build_classification_label(frame)
        self.assertTrue(result.loc[0, "label_quarantine"])
        self.assertEqual(result.loc[0, "quarantine_reason"], "cancelled")
        self.assertTrue(pd.isna(result.loc[0, "delay_label"]))

    def test_cause_tie_uses_fixed_order(self):
        frame = pd.DataFrame({
            "ArrDelay": [20],
            "CarrierDelay": [10],
            "WeatherDelay": [10],
            "NASDelay": [10],
            "SecurityDelay": [10],
            "LateAircraftDelay": [10],
        })
        result = build_classification_label(frame)
        self.assertEqual(result.loc[0, "delay_label"], "Delay_Carrier")

    def test_split_boundaries_are_included_in_their_blocks(self):
        frame = pd.DataFrame({
            "FlightDate": [
                "2024-08-31",
                "2024-09-01",
                "2024-10-31",
                "2024-11-01",
                "2024-12-31",
            ]
        })
        train, val, test = split_temporal(frame)
        self.assertEqual(len(train), 1)
        self.assertEqual(len(val), 2)
        self.assertEqual(len(test), 2)

    def test_bearing_uses_correct_atan2_arguments(self):
        north = compute_bearing(0.0, 0.0, 1.0, 0.0)
        east = compute_bearing(0.0, 0.0, 0.0, 1.0)
        self.assertAlmostEqual(north, 0.0, places=5)
        self.assertAlmostEqual(east, 90.0, places=5)


if __name__ == "__main__":
    unittest.main()
