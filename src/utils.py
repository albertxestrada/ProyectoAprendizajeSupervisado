"""
Utilidades comunes: logging, timing, memoria, reproducibilidad.

Responsable: Hector Gonzalez (cualquiera puede agregar helpers aqui)
"""

import time
import functools
import hashlib
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import RANDOM_STATE


def set_seed(seed: int = RANDOM_STATE):
    """Fija semillas para reproducibilidad."""
    np.random.seed(seed)
    try:
        import random
        random.seed(seed)
    except ImportError:
        pass


def timer(func):
    """Decorador que mide el tiempo de ejecucion."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"[TIMER] {func.__name__}: {elapsed:.2f}s")
        return result
    return wrapper


def df_summary(df: pd.DataFrame, name: str = "DataFrame"):
    """Imprime resumen rapido de un DataFrame: shape, memoria, nulos, dtypes."""
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    print(f"  Shape: {df.shape[0]:,} filas x {df.shape[1]} columnas")
    print(f"  Memoria: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
    print(f"  Nulos totales: {df.isnull().sum().sum():,}")
    print(f"  Dtypes: {dict(df.dtypes.value_counts())}")
    print(f"{'='*60}\n")


def file_sha256(filepath: str) -> str:
    """
    Calcula el hash SHA-256 de un archivo.
    Para el Data Contract de reproducibilidad.
    """
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def ensure_dir(path: str) -> Path:
    """Crea directorio si no existe y retorna Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
