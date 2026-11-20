"""
Features derivadas: viento, ciclicas, congestion, festivos.
Usado por: notebooks/03_preprocessing.ipynb

Responsable: Juan Camilo Bolanos
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import CORE_HUBS


# ============================================================================
# Coordenadas de los 20 Core Hubs FAA (lat, lon)
# Necesarias para calcular bearing y componente de viento
# ============================================================================
HUB_COORDS = {
    "ATL": (33.6407, -84.4277),
    "DFW": (32.8998, -97.0403),
    "DEN": (39.8561, -104.6737),
    "ORD": (41.9742, -87.9073),
    "LAX": (33.9425, -118.4081),
    "CLT": (35.2140, -80.9431),
    "MCO": (28.4312, -81.3081),
    "LAS": (36.0840, -115.1537),
    "PHX": (33.4373, -112.0078),
    "MIA": (25.7959, -80.2870),
    "SEA": (47.4502, -122.3088),
    "IAH": (29.9902, -95.3368),
    "JFK": (40.6413, -73.7781),
    "EWR": (40.6895, -74.1745),
    "SFO": (37.6213, -122.3790),
    "MSP": (44.8848, -93.2223),
    "BOS": (42.3656, -71.0096),
    "DTW": (42.2124, -83.3534),
    "FLL": (26.0742, -80.1506),
    "PHL": (39.8744, -75.2424),
}


def compute_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula el bearing (rumbo) en grados desde (lat1, lon1) a (lat2, lon2).
    Resultado en [0, 360).
    """
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dl = np.radians(lon2) - np.radians(lon1)
    x = np.sin(dl) * np.cos(p2)
    y = np.cos(p1) * np.sin(p2) - np.sin(p1) * np.cos(p2) * np.cos(dl)
    bearing = np.arctan2(y, x)+360
    return np.degrees(bearing) % 360


def add_flight_bearing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula el bearing (rumbo) de cada vuelo basado en origen y destino.
    Usa HUB_COORDS para obtener lat/lon. NaN si el aeropuerto no esta en la lista.

    Returns:
        DataFrame con nueva columna 'flight_bearing' (grados).
    """
    out = df.copy()
    lat = {k: v[0] for k, v in HUB_COORDS.items()}
    lon = {k: v[1] for k, v in HUB_COORDS.items()}
    o_lat, o_lon = out["Origin"].map(lat), out["Origin"].map(lon)
    d_lat, d_lon = out["Dest"].map(lat), out["Dest"].map(lon)
    out["flight_bearing"] = compute_bearing(o_lat, o_lon, d_lat, d_lon)
    return out


def add_headwind_component(
    df: pd.DataFrame,
    wind_speed_col: str = "wind_speed_250hPa",
    wind_dir_col: str = "wind_direction_250hPa",
) -> pd.DataFrame:
    """
    Calcula la componente de viento en cara/cola (headwind/tailwind)
    a nivel de crucero (250 hPa) respecto al rumbo del vuelo.

    Positivo = headwind (en contra), Negativo = tailwind (a favor).

    Returns:
        DataFrame con 'headwind_component' y 'crosswind_component'.
    """
    if "flight_bearing" not in df.columns:
        df = add_flight_bearing(df)
    out = df.copy()
    rel = np.radians(out[wind_dir_col] - out["flight_bearing"])
    out["headwind_component"] = out[wind_speed_col] * np.cos(rel)
    out["crosswind_component"] = out[wind_speed_col] * np.sin(rel)
    return out


def add_cyclical_time(df: pd.DataFrame, time_col: str = "CRSDepTime") -> pd.DataFrame:
    """
    Convierte la hora de salida en features ciclicas (sin/cos).
    Captura la periodicidad: 23:00 esta cerca de 01:00.

    Returns:
        DataFrame con 'hour_sin', 'hour_cos'.
    """
    out = df.copy()
    hhmm = pd.to_numeric(out[time_col], errors="coerce")
    hour = ((hhmm // 100) % 24) + (hhmm % 100) / 60
    out["hour_sin"] = np.sin(2 * np.pi * hour / 24)
    out["hour_cos"] = np.cos(2 * np.pi * hour / 24)
    return out


def add_day_of_week(df: pd.DataFrame, date_col: str = "FlightDate") -> pd.DataFrame:
    """
    Agrega dia de la semana como features ciclicas + is_weekend.

    Returns:
        DataFrame con 'dow_sin', 'dow_cos', 'is_weekend'.
    """
    out = df.copy()
    dow = pd.to_datetime(out[date_col]).dt.dayofweek
    out["dow_sin"] = np.sin(2 * np.pi * dow / 7)
    out["dow_cos"] = np.cos(2 * np.pi * dow / 7)
    out["is_weekend"] = (dow >= 5).astype(int)
    return out


def add_month_cyclical(df: pd.DataFrame, date_col: str = "FlightDate") -> pd.DataFrame:
    """
    Agrega mes como features ciclicas (estacionalidad).

    Returns:
        DataFrame con 'month_sin', 'month_cos'.
    """
    out = df.copy()
    month = pd.to_datetime(out[date_col]).dt.month
    out["month_sin"] = np.sin(2 * np.pi * month / 12)
    out["month_cos"] = np.cos(2 * np.pi * month / 12)
    return out


def add_holiday_flag(df: pd.DataFrame, date_col: str = "FlightDate") -> pd.DataFrame:
    """
    Marca si el vuelo cae en un dia festivo federal de EE.UU. o en su ventana (+/- 1 dia).

    Festivos federales 2024:
        New Year, MLK Day, Presidents Day, Memorial Day, Juneteenth,
        Independence Day, Labor Day, Columbus Day, Veterans Day,
        Thanksgiving, Christmas.

    Returns:
        DataFrame con 'is_holiday_window'.
    """
    from pandas.tseries.holiday import USFederalHolidayCalendar
    out = df.copy()
    dates = pd.to_datetime(out[date_col]).dt.normalize()
    holidays = USFederalHolidayCalendar().holidays(
        start=dates.min() - pd.Timedelta(days=2), end=dates.max() + pd.Timedelta(days=2))
    window = set()
    for holiday in holidays:
        window.update([holiday - pd.Timedelta(days=1), holiday, holiday + pd.Timedelta(days=1)])
    out["is_holiday_window"] = dates.isin(window).astype(int)
    return out


def add_hub_congestion(df: pd.DataFrame, date_col: str = "FlightDate") -> pd.DataFrame:
    """
    Calcula la congestion del hub: numero de vuelos en el mismo
    aeropuerto de origen en el mismo dia (proxy de congestion).

    Returns:
        DataFrame con 'origin_daily_flights'.
    """
    out = df.copy()
    out["origin_daily_flights"] = out.groupby(["Origin", date_col])["Origin"].transform("size")
    return out


def apply_all_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica toda la ingenieria de caracteristicas en orden.

    Orden sugerido:
        1. add_flight_bearing
        2. add_headwind_component
        3. add_cyclical_time
        4. add_day_of_week
        5. add_month_cyclical
        6. add_holiday_flag
        7. add_hub_congestion

    Args:
        df: DataFrame con vuelos ya mergeados con datos meteorologicos.

    Returns:
        DataFrame enriquecido con todas las features derivadas.
    """
    out = add_flight_bearing(df)
    if {"wind_speed_250hPa", "wind_direction_250hPa"} <= set(out.columns):
        out = add_headwind_component(out)
    out = add_cyclical_time(out)
    out = add_day_of_week(out)
    out = add_month_cyclical(out)
    out = add_holiday_flag(out)
    out = add_hub_congestion(out)
    return out
