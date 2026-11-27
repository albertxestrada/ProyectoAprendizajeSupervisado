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
# Zonas horarias por estado y excepciones de aeropuertos
# Cubre la poblacion completa, no solo los 20 hubs.
# ============================================================================
US_STATE_TIMEZONES = {
    "AL": "America/Chicago", "AR": "America/Chicago",
    "CT": "America/New_York", "DC": "America/New_York",
    "DE": "America/New_York", "FL": "America/New_York",
    "GA": "America/New_York", "IA": "America/Chicago",
    "IL": "America/Chicago", "IN": "America/Indiana/Indianapolis",
    "KS": "America/Chicago", "KY": "America/New_York",
    "LA": "America/Chicago",
    "MA": "America/New_York", "MD": "America/New_York",
    "ME": "America/New_York", "MI": "America/Detroit",
    "MN": "America/Chicago", "MO": "America/Chicago",
    "MS": "America/Chicago", "NC": "America/New_York",
    "NE": "America/Chicago", "NH": "America/New_York",
    "NJ": "America/New_York", "NY": "America/New_York",
    "OH": "America/New_York", "OK": "America/Chicago",
    "PA": "America/New_York", "RI": "America/New_York",
    "SC": "America/New_York", "TN": "America/Chicago",
    "TX": "America/Chicago", "VA": "America/New_York",
    "VT": "America/New_York", "WI": "America/Chicago",
    "WV": "America/New_York",
    "AZ": "America/Phoenix", "CO": "America/Denver",
    "ID": "America/Denver", "MT": "America/Denver",
    "NM": "America/Denver", "UT": "America/Denver",
    "WY": "America/Denver",
    "CA": "America/Los_Angeles", "NV": "America/Los_Angeles",
    "OR": "America/Los_Angeles", "WA": "America/Los_Angeles",
    "AK": "America/Anchorage", "HI": "Pacific/Honolulu",
    "PR": "America/Puerto_Rico", "VI": "America/St_Thomas",
    "ND": "America/Chicago", "SD": "America/Chicago",
}

# Zonas que no siguen el estado por completo o tienen codigo especial.
AIRPORT_TIMEZONE_OVERRIDES = {
    "PHX": "America/Phoenix", "HNL": "Pacific/Honolulu",
    "OGG": "Pacific/Honolulu", "KOA": "Pacific/Honolulu",
    "LIH": "Pacific/Honolulu", "SJU": "America/Puerto_Rico",
    "STT": "America/St_Thomas", "ELP": "America/Denver",
    "DEN": "America/Denver", "PHL": "America/New_York",
    "ATL": "America/New_York", "DFW": "America/Chicago",
    "ORD": "America/Chicago", "LAX": "America/Los_Angeles",
    "CLT": "America/New_York", "MCO": "America/New_York",
    "LAS": "America/Los_Angeles", "MIA": "America/New_York",
    "SEA": "America/Los_Angeles", "IAH": "America/Chicago",
    "JFK": "America/New_York", "EWR": "America/New_York",
    "SFO": "America/Los_Angeles", "MSP": "America/Chicago",
    "BOS": "America/New_York", "DTW": "America/New_York",
    "FLL": "America/New_York",
}

AIRPORT_TIMEZONES = AIRPORT_TIMEZONE_OVERRIDES.copy()


def get_airport_timezone(iata: str, state: str | None = None) -> str | None:
    """Resuelve la zona IANA de un aeropuerto por override o estado."""
    if iata in AIRPORT_TIMEZONE_OVERRIDES:
        return AIRPORT_TIMEZONE_OVERRIDES[iata]
    if state:
        return US_STATE_TIMEZONES.get(str(state).strip().upper())
    return None


def validate_airport_timezones(df: pd.DataFrame) -> None:
    """Exige zona horaria para todos los aeropuertos de origen y destino presentes."""
    for airport_col, state_col in (("Origin", "OriginState"), ("Dest", "DestState")):
        if airport_col not in df or state_col not in df:
            continue
        seen = df[[airport_col, state_col]].drop_duplicates()
        missing = [
            str(row[airport_col])
            for row in seen.to_dict("records")
            if get_airport_timezone(row[airport_col], row[state_col]) is None
        ]
        if missing:
            raise ValueError(
                "Aeropuertos sin zona IANA: " + ", ".join(sorted(set(missing)))
            )


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
    hours = (hhmm // 100).astype("Int64")
    minutes = (hhmm % 100).astype("Int64")

    flight_date = pd.to_datetime(out["FlightDate"], errors="coerce").dt.normalize()
    base_date = flight_date
    next_day = hours == 24
    base_date = base_date + pd.to_timedelta(next_day.fillna(False).astype(int), unit="D")
    hours = hours.where(~next_day, 0)
    local = (
        base_date
        + pd.to_timedelta(hours.astype("float64"), unit="h")
        + pd.to_timedelta(minutes.astype("float64"), unit="m")
    )
    validate_airport_timezones(out)
    utc = pd.Series(pd.NaT, index=out.index, dtype="datetime64[ns, UTC]")
    airport_state = dict(zip(out["Origin"], out["OriginState"])) if "OriginState" in out else {}
    for iata in out["Origin"].dropna().unique():
        tz = get_airport_timezone(iata, airport_state.get(iata))
        if tz is None:
            continue
        mask = out["Origin"] == iata
        if mask.any():
            loc = local[mask].dt.tz_localize(
                tz, ambiguous=False, nonexistent="shift_forward"
            )
            utc.loc[mask] = loc.dt.tz_convert("UTC")
    out["dep_datetime_utc"] = utc
    out["prediction_time_utc"] = utc - pd.Timedelta(hours=PREDICTION_HORIZON_H)
    out["pred_datetime_utc"] = out["prediction_time_utc"]
    out["T_corte_utc"] = out["prediction_time_utc"]

    if "CRSArrTime" in out.columns:
        arr_hhmm = pd.to_numeric(out["CRSArrTime"], errors="coerce")
        arr_hours = (arr_hhmm // 100).astype("Int64")
        arr_minutes = (arr_hhmm % 100).astype("Int64")
        dep_minutes = (
            pd.to_numeric(out["CRSDepTime"], errors="coerce").fillna(0)
        )
        dep_hours = dep_minutes // 100
        dep_clock_minutes = dep_minutes % 100
        arr_clock_minutes = arr_hours * 60 + arr_minutes
        dep_clock_minutes_total = dep_hours * 60 + dep_clock_minutes
        arr_next_day = (
            (arr_hours == 24)
            | (arr_clock_minutes < dep_clock_minutes_total)
        )
        arr_date = flight_date + pd.to_timedelta(
            arr_next_day.fillna(False).astype(int), unit="D"
        )
        arr_hours = arr_hours.where(~arr_next_day, 0)
        arr_local = (
            arr_date
            + pd.to_timedelta(arr_hours.astype("float64"), unit="h")
            + pd.to_timedelta(arr_minutes.astype("float64"), unit="m")
        )
        arr_utc = pd.Series(pd.NaT, index=out.index, dtype="datetime64[ns, UTC]")
        dest_state = (
            dict(zip(out["Dest"], out["DestState"]))
            if "DestState" in out else {}
        )
        for iata in out["Dest"].dropna().unique():
            tz = get_airport_timezone(iata, dest_state.get(iata))
            if tz is None:
                continue
            mask = out["Dest"] == iata
            if mask.any():
                loc = arr_local[mask].dt.tz_localize(
                    tz, ambiguous=False, nonexistent="shift_forward"
                )
                arr_utc.loc[mask] = loc.dt.tz_convert("UTC")
        out["arr_datetime_utc"] = arr_utc
    return out


def build_classification_label(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construye las etiquetas binarias y multiclase operadas.

    Logica:
    - Binaria: 1 si ArrDelay >= 15; 0 en caso contrario.
    - Los cancelados quedan en cuarentena y no reciben delay_label.
    - Si hay retraso, la causa es la columna con mas minutos.
    - El desempate usa el orden Carrier, Weather, NAS, Security, LateAircraft.
    - Si el retraso no tiene causa positiva, queda en cuarentena.

    IMPORTANTE: Ejecutar ANTES de eliminar columnas de leakage,
    porque necesita ArrDelay, CarrierDelay, etc. para construir la etiqueta.

    Args:
        df: DataFrame con columnas de demora originales de BTS.

    Returns:
        DataFrame con nueva columna 'delay_label'.
    """
    needed_cols = {"ArrDelay", "CarrierDelay",
                   "WeatherDelay", "NASDelay", "SecurityDelay", "LateAircraftDelay"}
    missing = sorted(needed_cols - set(df.columns))
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {missing}")

    out = df.copy()
    cause_columns = [
        "CarrierDelay",
        "WeatherDelay",
        "NASDelay",
        "SecurityDelay",
        "LateAircraftDelay",
    ]
    caused = out[cause_columns].fillna(0).clip(lower=0)
    cause_max = caused.max(axis=1)
    dominant = caused.idxmax(axis=1).map({
        "CarrierDelay": "Delay_Carrier",
        "WeatherDelay": "Delay_Weather",
        "NASDelay": "Delay_NAS",
        "SecurityDelay": "Delay_Security",
        "LateAircraftDelay": "Delay_LateAircraft"
    })
    out["is_delayed"] = out["ArrDelay"].ge(15).astype("int8")
    out["binary_delay"] = out["is_delayed"]

    cancelled = (
        out["Cancelled"].fillna(0).astype(float).eq(1)
        if "Cancelled" in out.columns
        else pd.Series(False, index=out.index)
    )
    missing_cause = out["is_delayed"].eq(1) & cause_max.eq(0)
    quarantined = cancelled | missing_cause

    out["cause_label"] = dominant.where(out["is_delayed"].eq(1))
    out["cause_label"] = out["cause_label"].where(~missing_cause)
    out["delay_label"] = pd.Series(pd.NA, index=out.index, dtype="object")
    out.loc[out["is_delayed"].eq(0) & ~cancelled, "delay_label"] = "OnTime"
    valid_delayed = out["is_delayed"].eq(1) & ~cancelled & ~missing_cause
    out.loc[valid_delayed, "delay_label"] = dominant[valid_delayed]
    out["label_quarantine"] = quarantined
    out["quarantine_reason"] = pd.Series(pd.NA, index=out.index, dtype="object")
    out.loc[cancelled, "quarantine_reason"] = "cancelled"
    out.loc[missing_cause, "quarantine_reason"] = "missing_delay_cause"

    assert set(out.loc[~out["label_quarantine"], "delay_label"].dropna()) <= set(
        CLASSIFICATION_LABELS
    )
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
    val = df[(d >= pd.Timestamp(VAL_START)) & (d <= pd.Timestamp(VAL_END))]
    test = df[d >= pd.Timestamp(TEST_START)]
    return train.copy(), val.copy(), test.copy()


def save_splits(train: pd.DataFrame, val: pd.DataFrame, test: pd.DataFrame) -> None:
    """Guarda los splits en parquet dentro de data/processed/splits/."""
    SPLITS_DIR.mkdir(parents=True, exist_ok=True)
    for name, part in [("train", train), ("val", val), ("test", test)]:
        part.to_parquet(SPLITS_DIR / f"{name}.parquet", index=False)
