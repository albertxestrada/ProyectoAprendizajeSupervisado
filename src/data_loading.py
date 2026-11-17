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


def load_bts(months: list[int] | None = None) -> pd.DataFrame:
    """
    Carga los CSVs mensuales de BTS On-Time Performance.

    Args:
        months: lista de meses a cargar (1-12). None = todos.

    Returns:
        DataFrame con todos los vuelos, sin columnas de leakage.

    TODO (Juan Camilo):
        - Leer todos los CSVs de data/raw/bts/
        - Si months no es None, filtrar por columna 'Month'
        - Concatenar en un solo DataFrame
        - Eliminar columnas de LEAKAGE_COLUMNS que existan en el df
        - Manejar el caso de que no haya archivos (FileNotFoundError)
    """
    raise NotImplementedError("Pendiente: Juan Camilo")


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
    raise NotImplementedError("Pendiente: Juan Camilo")


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
    raise NotImplementedError("Pendiente: Juan Camilo")
