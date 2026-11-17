"""
Limpieza, join temporal y encoding.
Usado por: notebooks/03_preprocessing.ipynb

Responsable: Juan Camilo Bolanos
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import (
    CLASSIFICATION_LABELS,
    TRAIN_END,
    VAL_START,
    VAL_END,
    TEST_START,
    SPLITS_DIR,
)


# ============================================================================
# Zonas horarias por aeropuerto (20 Core Hubs FAA)
# Necesario para convertir CRSDepTime (hora local) a UTC
# ============================================================================
AIRPORT_TIMEZONES = {
    "ATL": "America/New_York",
    "DFW": "America/Chicago",
    "DEN": "America/Denver",
    "ORD": "America/Chicago",
    "LAX": "America/Los_Angeles",
    "CLT": "America/New_York",
    "MCO": "America/New_York",
    "LAS": "America/Los_Angeles",
    "PHX": "America/Phoenix",
    "MIA": "America/New_York",
    "SEA": "America/Los_Angeles",
    "IAH": "America/Chicago",
    "JFK": "America/New_York",
    "EWR": "America/New_York",
    "SFO": "America/Los_Angeles",
    "MSP": "America/Chicago",
    "BOS": "America/New_York",
    "DTW": "America/New_York",
    "FLL": "America/New_York",
    "PHL": "America/New_York",
}


def convert_crs_to_utc(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte CRSDepTime (hora local HHMM) a un datetime UTC completo.
    Usa la zona horaria del aeropuerto de origen.

    Args:
        df: DataFrame con columnas FlightDate, CRSDepTime, Origin.

    Returns:
        DataFrame con nueva columna 'dep_datetime_utc'.

    TODO (Juan Camilo):
        - CRSDepTime es entero HHMM (ej. 1430 = 14:30, 2400 = medianoche)
        - Combinar FlightDate + hora/minuto para crear datetime local naive
        - Usar AIRPORT_TIMEZONES para localizar a la zona del aeropuerto de origen
        - Convertir a UTC
        - Manejar 'ambiguous' (cambio de horario) y 'nonexistent'
    """
    raise NotImplementedError("Pendiente: Juan Camilo")


def build_classification_label(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construye la etiqueta multiclase de clasificacion (8 clases).

    Logica:
    - Si cancelado: Cancel_Carrier (A), Cancel_Weather (B), Cancel_NAS (C)
    - Si ArrDelay > 15 min: la causa dominante (CarrierDelay, WeatherDelay,
      NASDelay, LateAircraftDelay)
    - Si no: OnTime

    IMPORTANTE: Ejecutar ANTES de eliminar columnas de leakage,
    porque necesita ArrDelay, CarrierDelay, etc. para construir la etiqueta.

    Args:
        df: DataFrame con columnas de demora originales de BTS.

    Returns:
        DataFrame con nueva columna 'delay_label'.

    TODO (Juan Camilo):
        - Usar np.select con condiciones en orden de prioridad
        - Clases: ver config.CLASSIFICATION_LABELS
        - Verificar que las columnas de demora existen antes de usarlas
    """
    raise NotImplementedError("Pendiente: Juan Camilo")


def separate_cancelled_operated(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Separa vuelos cancelados (solo clasificacion) de operados (ambas tareas).

    Returns:
        (df_operated, df_cancelled)
    """
    raise NotImplementedError("Pendiente: Juan Camilo")


def temporal_join_weather(
    flights: pd.DataFrame,
    weather: pd.DataFrame,
    weather_time_col: str = "time",
    weather_station_col: str = "station",
    window_hours: int = 4,
    direction: str = "backward",
) -> pd.DataFrame:
    """
    Join temporal entre vuelos y datos meteorologicos usando pd.merge_asof.
    Para cada vuelo, busca la observacion meteorologica mas cercana
    dentro de la ventana temporal especificada.

    Args:
        flights: DataFrame con 'dep_datetime_utc' y 'Origin'.
        weather: DataFrame con timestamp UTC y codigo de estacion.
        window_hours: tamano de la ventana de busqueda (default 4h = antes del vuelo).
        direction: 'backward' (solo datos previos al vuelo).

    Returns:
        DataFrame de vuelos enriquecido con columnas meteorologicas.

    TODO (Juan Camilo):
        - Ordenar ambos DataFrames por sus columnas de tiempo
        - Usar pd.merge_asof con tolerance y direction
        - Mergear por aeropuerto (left_by='Origin', right_by=weather_station_col)
    """
    raise NotImplementedError("Pendiente: Juan Camilo")


def split_temporal(
    df: pd.DataFrame,
    date_col: str = "FlightDate",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Separacion cronologica train/val/test.
    Fechas definidas en config.py:
        Train: ene-ago 2024, Val: sep-oct 2024, Test: nov-dic 2024

    Returns:
        (train, val, test)
    """
    raise NotImplementedError("Pendiente: Juan Camilo")


def save_splits(train: pd.DataFrame, val: pd.DataFrame, test: pd.DataFrame) -> None:
    """Guarda los splits en parquet dentro de data/processed/splits/."""
    raise NotImplementedError("Pendiente: Juan Camilo")
