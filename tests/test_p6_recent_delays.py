import unittest

import pandas as pd

from src.feature_engineering import recent_delays


class P6RecentDelaysTests(unittest.TestCase):
    def test_window_excludes_future_flights_and_other_airlines(self):
        frame = pd.DataFrame({
            "Reporting_Airline": ["AA", "AA", "AA", "DL", "AA"],
            "Origin": ["ATL", "ATL", "ATL", "ATL", "ATL"],
            "T_corte_utc": pd.to_datetime([
                "2024-07-01T12:00Z",
                "2024-07-01T12:00Z",
                "2024-07-01T12:00Z",
                "2024-07-01T12:00Z",
                "2024-07-01T12:00Z",
            ], utc=True),
            "arr_datetime_utc": pd.to_datetime([
                "2024-07-01T10:30Z",
                "2024-07-01T10:45Z",
                "2024-07-01T11:30Z",
                "2024-07-01T11:15Z",
                "2024-07-01T12:30Z",
            ], utc=True),
            "ArrDelay": [30, -10, 20, 60, 999],
            "Cancelled": [0, 0, 0, 0, 0],
        })
        result = recent_delays(frame)
        self.assertEqual(result.loc[0, "recent_flight_count"], 2)
        self.assertEqual(result.loc[0, "recent_delay_median"], 5.0)
        self.assertEqual(result.loc[0, "recent_delay_rate"], 0.5)
        self.assertEqual(result.loc[3, "recent_flight_count"], 0)
        self.assertEqual(result.loc[4, "recent_flight_count"], 3)

    def test_cancelled_flight_uses_accumulated_delay(self):
        frame = pd.DataFrame({
            "Reporting_Airline": ["AA", "AA"],
            "Origin": ["ATL", "ATL"],
            "T_corte_utc": pd.to_datetime([
                "2024-07-01T12:00Z",
                "2024-07-01T12:00Z",
            ], utc=True),
            "arr_datetime_utc": pd.to_datetime([
                "2024-07-01T11:30Z",
                "2024-07-01T11:00Z",
            ], utc=True),
            "ArrDelay": [0, None],
            "Cancelled": [0, 1],
        })
        result = recent_delays(frame)
        self.assertEqual(result.loc[0, "recent_flight_count"], 1)
        self.assertEqual(result.loc[0, "recent_delay_median"], 60.0)
        self.assertEqual(result.loc[0, "recent_delay_rate"], 1.0)

    def test_no_history_returns_zero_summary(self):
        frame = pd.DataFrame({
            "Reporting_Airline": ["AA"],
            "Origin": ["ATL"],
            "T_corte_utc": pd.to_datetime(["2024-07-01T12:00Z"], utc=True),
            "arr_datetime_utc": pd.to_datetime(["2024-07-01T11:30Z"], utc=True),
            "ArrDelay": [10],
            "Cancelled": [0],
        })
        result = recent_delays(frame)
        self.assertEqual(result.loc[0, "recent_flight_count"], 0)
        self.assertEqual(result.loc[0, "recent_delay_median"], 0.0)
        self.assertEqual(result.loc[0, "recent_delay_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
