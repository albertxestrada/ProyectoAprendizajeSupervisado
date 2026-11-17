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

    TODO (Juan Camilo):
        - Usar la formula esferica del bearing inicial
        - Convertir a radianes, aplicar arctan2, devolver en grados [0, 360)
    """
    raise NotImplementedError("Pendiente: Juan Camilo")


def add_flight_bearing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula el bearing (rumbo) de cada vuelo basado en origen y destino.
    Usa HUB_COORDS para obtener lat/lon. NaN si el aeropuerto no esta en la lista.

    Returns:
        DataFrame con nueva columna 'flight_bearing' (grados).
    """
    raise NotImplementedError("Pendiente: Juan Camilo")


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

    TODO (Juan Camilo):
        - Requiere 'flight_bearing' (ejecutar add_flight_bearing antes)
        - relative_angle = wind_direction - flight_bearing
        - headwind = wind_speed * cos(relative_angle)
        - crosswind = wind_speed * sin(relative_angle)
    """
    raise NotImplementedError("Pendiente: Juan Camilo")


def add_cyclical_time(df: pd.DataFrame, time_col: str = "CRSDepTime") -> pd.DataFrame:
    """
    Convierte la hora de salida en features ciclicas (sin/cos).
    Captura la periodicidad: 23:00 esta cerca de 01:00.

    Returns:
        DataFrame con 'hour_sin', 'hour_cos'.
    """
    raise NotImplementedError("Pendiente: Juan Camilo")


def add_day_of_week(df: pd.DataFrame, date_col: str = "FlightDate") -> pd.DataFrame:
    """
    Agrega dia de la semana como features ciclicas + is_weekend.

    Returns:
        DataFrame con 'dow_sin', 'dow_cos', 'is_weekend'.
    """
    raise NotImplementedError("Pendiente: Juan Camilo")


def add_month_cyclical(df: pd.DataFrame, date_col: str = "FlightDate") -> pd.DataFrame:
    """
    Agrega mes como features ciclicas (estacionalidad).

    Returns:
        DataFrame con 'month_sin', 'month_cos'.
    """
    raise NotImplementedError("Pendiente: Juan Camilo")


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
    raise NotImplementedError("Pendiente: Juan Camilo")


def add_hub_congestion(df: pd.DataFrame, date_col: str = "FlightDate") -> pd.DataFrame:
    """
    Calcula la congestion del hub: numero de vuelos en el mismo
    aeropuerto de origen en el mismo dia (proxy de congestion).

    Returns:
        DataFrame con 'origin_daily_flights'.
    """
    raise NotImplementedError("Pendiente: Juan Camilo")


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
    raise NotImplementedError("Pendiente: Juan Camilo")
