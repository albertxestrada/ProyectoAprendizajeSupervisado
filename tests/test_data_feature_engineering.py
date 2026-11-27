import unittest

import pandas as pd

from src.data_loading import load_bts, load_iem, load_open_meteo
from src.feature_engineering import (
    add_cyclical_time,
    add_flight_bearing,
    add_hub_congestion,
    apply_all_features,
    compute_bearing,
)
from src.preprocessing import (
    build_classification_label,
    convert_crs_to_utc,
    split_temporal,
)


class DataFeatureEngineeringTests(unittest.TestCase):
    def test_real_data_loaders(self):
        bts = load_bts(months=[2], drop_leakage=False)
        open_meteo = load_open_meteo()
        iem = load_iem()

        self.assertEqual(len(bts) > 500_000, True)
        self.assertIn("FlightDate", bts.columns)
        self.assertIn("Cancelled", bts.columns)
        self.assertEqual(open_meteo["airport"].nunique(), 20)
        self.assertIn("timestamp_utc", open_meteo.columns)
        self.assertEqual(iem["station"].nunique(), 20)
        self.assertIn("time", iem.columns)

    def test_label_is_at_least_fifteen_minutes(self):
        df = pd.DataFrame({
            "Cancelled": [0, 0, 0],
            "CancellationCode": [None, None, None],
            "ArrDelay": [14.0, 15.0, None],
            "CarrierDelay": [0.0, 20.0, 0.0],
            "WeatherDelay": [0.0, 0.0, 0.0],
            "NASDelay": [0.0, 0.0, 0.0],
            "LateAircraftDelay": [0.0, 0.0, 0.0],
        })
        labels = build_classification_label(df)["delay_label"]
        self.assertEqual(labels.iloc[0], "OnTime")
        self.assertEqual(labels.iloc[1], "Delay_Carrier")
        self.assertEqual(labels.iloc[2], "OnTime")

    def test_2400_becomes_next_day_in_utc(self):
        df = pd.DataFrame({
            "FlightDate": pd.to_datetime(["2024-06-01"]),
            "CRSDepTime": [2400],
            "Origin": ["ATL"],
        })
        result = convert_crs_to_utc(df)
        dep = result["dep_datetime_utc"].iloc[0]
        pred = result["prediction_time_utc"].iloc[0]
        self.assertEqual(dep.strftime("%Y-%m-%d %H:%M"), "2024-06-02 04:00")
        self.assertEqual(pred.strftime("%Y-%m-%d %H:%M"), "2024-06-02 00:00")

    def test_split_boundaries(self):
        df = pd.DataFrame({"FlightDate": pd.to_datetime([
            "2024-08-31", "2024-09-01", "2024-10-31", "2024-11-01",
        ])})
        train, val, test = split_temporal(df)
        self.assertEqual(len(train), 1)
        self.assertEqual(len(val), 2)
        self.assertEqual(len(test), 1)

    def test_bearing_and_features(self):
        north = compute_bearing(0, 0, 1, 0)
        east = compute_bearing(0, 0, 0, 1)
        self.assertAlmostEqual(north, 0.0, places=6)
        self.assertAlmostEqual(east, 90.0, places=6)

        df = pd.DataFrame({
            "FlightDate": pd.to_datetime(["2024-01-01"]),
            "CRSDepTime": [600],
            "Origin": ["ATL"],
            "Dest": ["DFW"],
        })
        featured = add_flight_bearing(df)
        featured = add_cyclical_time(featured)
        featured = add_hub_congestion(featured)
        self.assertIn("flight_bearing", featured.columns)
        self.assertIn("hour_sin", featured.columns)
        self.assertIn("origin_daily_flights", featured.columns)

    def test_apply_all_features_accepts_suffixed_wind_columns(self):
        df = pd.DataFrame({
            "FlightDate": pd.to_datetime(["2024-01-01"]),
            "CRSDepTime": [600],
            "Origin": ["ATL"],
            "Dest": ["DFW"],
            "wind_speed_250hPa_250hpa": [50.0],
            "wind_direction_250hPa_250hpa": [90.0],
        })
        featured = apply_all_features(df)
        self.assertIn("headwind_component", featured.columns)
        self.assertIn("crosswind_component", featured.columns)


if __name__ == "__main__":
    unittest.main()
