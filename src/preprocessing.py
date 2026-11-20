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

PREDICTION_HORIZON_H = 4
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
    """
    out = df.copy()
    hhmm = pd.to_numeric(out["CRSDepTime"], errors="coerce")
    hours = (hhmm//100).astype(64)
    minutes = (hhmm%100).astype(64)

    hours = hours.where(hours != 24, 0)
    local = (pd.to_datetime(out["FlightDate"]).dt.normalize() 
             + pd.to_timedelta(hours.astype("float"), unit="h")
             + pd.to_timedelta(minutes.astype("float"), unit="m"))
    utc = pd.Series(pd.NaT, index=out.index, dtype="datetime64[ns, UTC]")
    for iata,tz in AIRPORT_TIMEZONES.items():
        mask = out["Origin"] == iata
        if mask.any():
            loc = local[mask].dt.tz_localize(tz, ambiguous=False, nonexistent="shift_forward")
            utc.loc[mask] = loc.dt.tz_convert("UTC")
    out["dep_datetime_utc"] = utc
    out["pred_datetime_utc"] = utc - pd.Timedelta(hours = PREDICTION_HORIZON_H)
    return out


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
    """
    needed_cols = ["Cancelled", "CancellationCode", "ArrDelay", "CarrierDelay",
                   "WeatherDelay", "NASDelay", "LateAircraftDelay"]
    missing = needed_cols - set(df.columns)
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {missing}")

    out = df.copy()
    caused = out[["CarrierDelay", "WeatherDelay", "NASDelay", "LateAircraftDelay"]].fillna(0)
    dominant = caused.idxmax(axis=1).map({
        "CarrierDelay": "Delay_Carrier",
        "WeatherDelay": "Delay_Weather",
        "NASDelay": "Delay_NAS",
        "LateAircraftDelay": "Delay_LateAircraft"
    })
    dominant = dominant.where(caused.max(axis=1) > 0, "Delay_Carrier")

    cancelled = out["Cancelled"].fillna(0).astype(float)==1
    cancel_label = out["CancellationCode"].map({
        "A": "Cancel_Carrier",
        "B": "Cancel_Weather",
        "C": "Cancel_NAS"
    })
    delayed = (out["ArrDelay"] > 15)
    out["delay_label"] = np.select(
        [cancelled & cancel_label.notna(), delayed],
        [cancel_label, dominant],
        default="OnTime"
    )
    assert set(out["delay_label"]) <= set(CLASSIFICATION_LABELS)
    return out


def separate_cancelled_operated(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Separa vuelos cancelados (solo clasificacion) de operados (ambas tareas).

    Returns:
        (df_operated, df_cancelled)
    """
    cancelled_mask = df["Cancelled"].fillna(0).astype(float)==1
    operated_mask = ~cancelled_mask & df["AirTime"].notna()
    return df[operated_mask].copy(), df[cancelled_mask].copy()


def temporal_join_weather(
    flights: pd.DataFrame,
    weather: pd.DataFrame,
    weather_time_col: str = "time",
    weather_station_col: str = "station",
    window_hours: int = 4,
    direction: str = "backward",
    flight_time_col: str = "prediction_time_utc",
    suffix: str = "",
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
    """
    left = flights.dropna(subset=[flight_time_col]).copy()
    right = weather.copy()

    left[flight_time_col] = left[flight_time_col].astype("datetime64[ns, UTC]")
    right[weather_time_col] = right[weather_time_col].astype("datetime64[ns, UTC]")
    left = left.sort_values(flight_time_col)
    right = right.sort_values(weather_time_col)
    if suffix:
        right = right.rename(columns={c: f"{c}{suffix}" for c in right.columns
                                      if c not in (weather_time_col, weather_station_col)})

    merged = pd.merge_asof(
        left, right,
        left_on=flight_time_col,
        right_on=weather_time_col,
        left_by="Origin",
        right_by=weather_station_col,
        direction=direction,
        tolerance=pd.Timedelta(hours=window_hours)
    )
    return merged.drop(columns=[weather_time_col], errors="ignore")


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
    d = pd.to_datetime(df[date_col])
    train = df[d <= pd.Timestamp(TRAIN_END)]
    val = df[(d > pd.Timestamp(VAL_START)) & (d <= pd.Timestamp(VAL_END))]
    test = df[d > pd.Timestamp(TEST_START)]
    return train.copy(), val.copy(), test.copy()


def save_splits(train: pd.DataFrame, val: pd.DataFrame, test: pd.DataFrame) -> None:
    """Guarda los splits en parquet dentro de data/processed/splits/."""
    SPLITS_DIR.mkdir(parents=True, exist_ok=True)
    for name, part in [("train", train), ("val", val), ("test", test)]:
        part.to_parquet(SPLITS_DIR / f"{name}.parquet", index=False)
