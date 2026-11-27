import unittest

import pandas as pd

from src.preprocessing import (
    convert_crs_to_utc,
    get_airport_timezone,
)


class P4TimezoneTests(unittest.TestCase):
    def test_four_hour_cutoff_is_in_utc(self):
        frame = pd.DataFrame({
            "FlightDate": ["2024-07-01"],
            "CRSDepTime": [1200],
            "Origin": ["ATL"],
            "OriginState": ["GA"],
            "CRSArrTime": [1500],
            "Dest": ["DFW"],
            "DestState": ["TX"],
        })
        result = convert_crs_to_utc(frame)
        self.assertEqual(
            result.loc[0, "dep_datetime_utc"],
            pd.Timestamp("2024-07-01T16:00:00Z"),
        )
        self.assertEqual(
            result.loc[0, "T_corte_utc"],
            pd.Timestamp("2024-07-01T12:00:00Z"),
        )

    def test_2400_moves_departure_to_next_day(self):
        frame = pd.DataFrame({
            "FlightDate": ["2024-07-01"],
            "CRSDepTime": [2400],
            "Origin": ["DEN"],
            "OriginState": ["CO"],
            "CRSArrTime": [230],
            "Dest": ["ORD"],
            "DestState": ["IL"],
        })
        result = convert_crs_to_utc(frame)
        self.assertEqual(
            result.loc[0, "dep_datetime_utc"],
            pd.Timestamp("2024-07-02T06:00:00Z"),
        )
        self.assertEqual(
            result.loc[0, "arr_datetime_utc"],
            pd.Timestamp("2024-07-02T05:30:00Z"),
        )

    def test_state_and_airport_timezone_resolution(self):
        self.assertEqual(get_airport_timezone("ATL", "GA"), "America/New_York")
        self.assertEqual(get_airport_timezone("DFW", "TX"), "America/Chicago")
        self.assertEqual(get_airport_timezone("DEN", "CO"), "America/Denver")
        self.assertEqual(get_airport_timezone("LAX", "CA"), "America/Los_Angeles")
        self.assertEqual(get_airport_timezone("PHX", "AZ"), "America/Phoenix")

    def test_missing_airport_timezone_is_rejected(self):
        frame = pd.DataFrame({
            "FlightDate": ["2024-07-01"],
            "CRSDepTime": [1200],
            "Origin": ["XXX"],
            "OriginState": ["ZZ"],
        })
        with self.assertRaises(ValueError):
            convert_crs_to_utc(frame)


if __name__ == "__main__":
    unittest.main()
