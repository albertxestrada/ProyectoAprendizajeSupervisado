import unittest

import pandas as pd

from src.feature_engineering import add_scheduled_congestion


class P7ScheduledCongestionTests(unittest.TestCase):
    def test_cancelled_flights_are_included(self):
        frame = pd.DataFrame({
            "Origin": ["ATL", "ATL", "ATL", "DFW"],
            "Dest": ["DFW", "BOS", "MIA", "ATL"],
            "Cancelled": [0, 1, 0, 0],
            "dep_datetime_utc": pd.to_datetime([
                "2024-07-01T12:10Z",
                "2024-07-01T12:40Z",
                "2024-07-01T13:10Z",
                "2024-07-01T12:20Z",
            ], utc=True),
            "arr_datetime_utc": pd.to_datetime([
                "2024-07-01T14:10Z",
                "2024-07-01T15:40Z",
                "2024-07-01T16:10Z",
                "2024-07-01T14:20Z",
            ], utc=True),
        })
        result = add_scheduled_congestion(frame)

        self.assertEqual(result.loc[0, "origin_scheduled_departures_hour"], 2)
        self.assertEqual(result.loc[0, "origin_hour_congestion"], 3)
        self.assertEqual(result.loc[0, "dest_scheduled_arrivals_hour"], 1)
        self.assertEqual(result.loc[0, "dest_hour_congestion"], 2)

    def test_missing_cancelled_column_is_not_required_for_congestion(self):
        frame = pd.DataFrame({
            "Origin": ["ATL"],
            "Dest": ["DFW"],
            "dep_datetime_utc": pd.to_datetime(["2024-07-01T12:10Z"], utc=True),
            "arr_datetime_utc": pd.to_datetime(["2024-07-01T14:10Z"], utc=True),
        })
        result = add_scheduled_congestion(frame)
        self.assertEqual(result.loc[0, "scheduled_departures_hour"], 1)
        self.assertEqual(result.loc[0, "scheduled_arrivals_hour"], 1)

    def test_missing_utc_columns_fail_explicitly(self):
        frame = pd.DataFrame({"Origin": ["ATL"], "Dest": ["DFW"]})
        with self.assertRaises(ValueError):
            add_scheduled_congestion(frame)


if __name__ == "__main__":
    unittest.main()
