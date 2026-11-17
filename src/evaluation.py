"""
Metricas, visualizaciones y comparacion de modelos.
Usado por: notebooks/04_classification.ipynb, notebooks/05_regression.ipynb

Responsables:
    - Funciones de clasificacion: Alberto Estrada
    - Funciones de regresion: Dylan Cantillo
    - model_comparison_table / save_comparison_table: Hector Gonzalez
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import CLASSIFICATION_LABELS, TARGET_MAE, TARGET_MACRO_F1, RESULTS_DIR


# ============================================================================
# Metricas de Clasificacion — Alberto
# ============================================================================

def classification_metrics(y_true, y_pred, labels=CLASSIFICATION_LABELS) -> dict:
    """
    Calcula metricas de clasificacion principales.

    Returns:
        dict con accuracy, macro_f1, weighted_f1, per_class_report, meets_target.

    TODO (Alberto):
        - Usar sklearn: accuracy_score, f1_score, classification_report
        - meets_target = macro_f1 >= TARGET_MACRO_F1
    """
    raise NotImplementedError("Pendiente: Alberto")


def plot_confusion_matrix(y_true, y_pred, labels=CLASSIFICATION_LABELS,
                          title="Confusion Matrix", save_path=None,
                          normalize=True):
    """
    Genera y guarda la matriz de confusion.
    Si normalize=True, muestra porcentajes por fila (recall por clase).

    TODO (Alberto):
        - Usar sklearn.metrics.confusion_matrix + seaborn.heatmap
        - Guardar figura si save_path no es None
    """
    raise NotImplementedError("Pendiente: Alberto")


def plot_per_class_f1(y_true, y_pred, labels=CLASSIFICATION_LABELS,
                      title="F1-Score por Clase", save_path=None):
    """
    Grafico de barras con F1 por cada clase de retraso.
    Incluir linea horizontal del TARGET_MACRO_F1 como referencia.

    TODO (Alberto):
        - classification_report con output_dict=True
        - Grafico de barras + axhline del target
    """
    raise NotImplementedError("Pendiente: Alberto")


# ============================================================================
# Metricas de Regresion — Dylan
# ============================================================================

def regression_metrics(y_true, y_pred) -> dict:
    """
    Calcula metricas de regresion principales.

    Returns:
        dict con mae, rmse, r2, mape, meets_target.

    TODO (Dylan):
        - Usar sklearn: mean_absolute_error, mean_squared_error, r2_score
        - MAPE manual evitando division por 0
        - meets_target = mae <= TARGET_MAE
    """
    raise NotImplementedError("Pendiente: Dylan")


def plot_predicted_vs_actual(y_true, y_pred, title="Predicted vs Actual AirTime",
                             save_path=None):
    """
    Scatter plot de prediccion vs real con linea de identidad (perfecto).

    TODO (Dylan):
        - Scatter con alpha bajo (muchos puntos)
        - Linea roja y=x como referencia
    """
    raise NotImplementedError("Pendiente: Dylan")


def plot_residuals(y_true, y_pred, title="Distribucion de Residuos",
                   save_path=None):
    """
    Histograma de residuos + scatter residuos vs valor real.

    TODO (Dylan):
        - Subplot 1: histograma de (y_pred - y_true)
        - Subplot 2: scatter y_true vs residuo, linea en 0
    """
    raise NotImplementedError("Pendiente: Dylan")


# ============================================================================
# Comparacion de Modelos — Hector
# ============================================================================

def model_comparison_table(results: dict, task: str = "classification") -> pd.DataFrame:
    """
    Genera tabla comparativa de modelos.

    Args:
        results: dict {nombre_modelo: dict_metricas}
        task: 'classification' o 'regression'

    Returns:
        DataFrame ordenado por metrica principal (macro_f1 desc o mae asc).

    TODO (Hector):
        - Crear DataFrame a partir del dict
        - Ordenar segun la tarea
    """
    raise NotImplementedError("Pendiente: Hector")


def save_comparison_table(df: pd.DataFrame, save_path: str):
    """
    Guarda tabla comparativa en CSV y Markdown.

    TODO (Hector):
        - df.to_csv() y df.to_markdown()
        - Crear directorio padre si no existe
    """
    raise NotImplementedError("Pendiente: Hector")
