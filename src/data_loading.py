"""
Carga y parseo de las 3 fuentes de datos.
Usado por: notebooks/01_eda_bts.ipynb, notebooks/02_eda_weather.ipynb, notebooks/03_preprocessing.ipynb

Responsable: Juan Camilo Bolanos
"""

import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import RAW_DIR, LEAKAGE_COLUMNS

def _read_all(subdir: str) -> pd.DataFrame:
    """
    Lee todos los CSVs de un subdirectorio de RAW_DIR y los concatena en un solo DataFrame.
    """
    path = RAW_DIR / subdir
    files = sorted(path.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No hay csv en {path}")
    return pd.concat((pd.read_csv(f, low_memory=False) for f in files), ignore_index=True)


def load_bts(months: list[int] | None = None, drop_leakage: bool = False) -> pd.DataFrame:
    """
    Carga los CSVs mensuales de BTS On-Time Performance.

    Args:
        months: lista de meses a cargar (1-12). None = todos.

    Returns:
        DataFrame con todos los vuelos, sin columnas de leakage.
    """

    files = sorted((RAW_DIR/"bts").glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No hay csv de BTS en {RAW_DIR/'bts'}")
    df = pd.concat((pd.read_csv(f,low_memory=False)for f in files),ignore_index=True)
    df["FlightDate"] = pd.to_datetime(df["FlightDate"])

    if months is not None:
        df = df[df["FlightDate"].dt.month.isin(months)]
    if drop_leakage:
        df = df.drop(columns=[c for c in LEAKAGE_COLUMNS if c in df.columns])
    return df.reset_index(drop=True)


def load_open_meteo() -> pd.DataFrame:
    """
    Carga los pronosticos numericos de Open-Meteo Previous Runs API.
    Vientos a 250 hPa (jet stream).

    Returns:
        DataFrame con pronosticos por aeropuerto y timestamp UTC.

    TODO (Juan Camilo):
        - Leer CSVs de data/raw/open_meteo/
        - Parsear columna 'time' a datetime UTC
        - Concatenar si hay multiples archivos
    """
    df = _read_all("open_meteo")
    df = df.rename(columns={
        "time": "timestamp_utc",
        "timestamp": "timestamp_utc",
        "station": "airport",
    })
    if "timestamp_utc" not in df.columns:
        raise ValueError("Open-Meteo no contiene una columna de tiempo reconocible")
    if "airport" not in df.columns:
        raise ValueError("Open-Meteo no contiene una columna de aeropuerto reconocible")
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp_utc"])
    df["station"] = df["airport"]
    return df.sort_values(["airport", "timestamp_utc"]).reset_index(drop=True)


def load_iem() -> pd.DataFrame:
    """
    Carga las observaciones ASOS/METAR del IEM.
    Techo de nubes y visibilidad en aeropuertos.

    Returns:
        DataFrame con observaciones, tipos corregidos (centinelas M -> NaN).

    TODO (Juan Camilo):
        - Leer CSVs de data/raw/iem/
        - Reemplazar centinelas "M" por NaN en columnas numericas
        - Convertir columnas object a float64 donde corresponda
        - Parsear columna 'valid' a datetime UTC
    """
    df = _read_all("iem")
    df = df.rename(columns={
        "valid": "time",
        "station": "station_icao",
        "airport_iata": "station",
    })
    df["time"] = pd.to_datetime(df["time"], utc=True, errors="coerce")
    df = df.dropna(subset=["time"])

    for col in df.columns:
        if col in {"time", "station", "station_icao"}:
            continue
        if pd.api.types.is_object_dtype(df[col].dtype) or pd.api.types.is_string_dtype(df[col].dtype):
            cleaned = df[col].replace({"M": pd.NA, "T": pd.NA})
            numeric = pd.to_numeric(cleaned, errors="coerce")
            if cleaned.notna().sum() > 0 and numeric.notna().sum() >= 0.9 * cleaned.notna().sum():
                df[col] = numeric.astype("float64")
            else:
                df[col] = cleaned
    return df.sort_values(["station", "time"]).reset_index(drop=True)