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
    from sklearn.metrics import accuracy_score, f1_score, classification_report
    
    report = classification_report(y_true, y_pred, labels=labels, 
                                   output_dict=True, zero_division=0)
    macro = f1_score(y_true, y_pred, average="macro", zero_division=0)
    
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "macro_f1": macro,
        "weighted_f1": f1_score(y_true, y_pred, average="weighted", zero_division=0),
        "per_class_report": report,
        "meets_target": macro >= TARGET_MACRO_F1,
    }


def plot_confusion_matrix(y_true, y_pred, labels=CLASSIFICATION_LABELS,
                          title="Confusion Matrix", save_path=None,
                          normalize=True):
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.metrics import confusion_matrix
    
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    
    if normalize:
        cm_display = cm.astype("float") / cm.sum(axis=1, keepdims=True)
        cm_display = np.nan_to_num(cm_display)
        fmt = ".2%"
    else:
        cm_display = cm
        fmt = "d"
    
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(cm_display, annot=True, fmt=fmt, cmap="Blues",
                xticklabels=labels, yticklabels=labels, ax=ax)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title(title)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    
    if save_path:
        from pathlib import Path
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    
    plt.show()
    return fig


def plot_per_class_f1(y_true, y_pred, labels=CLASSIFICATION_LABELS,
                      title="F1-Score por Clase", save_path=None):
    import matplotlib.pyplot as plt
    from sklearn.metrics import classification_report
    
    report = classification_report(y_true, y_pred, labels=labels,
                                   output_dict=True, zero_division=0)
    
    classes = [l for l in labels if l in report]
    f1_scores = [report[l]["f1-score"] for l in classes]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(classes, f1_scores, color="steelblue", edgecolor="white")
    ax.axhline(y=TARGET_MACRO_F1, color="red", linestyle="--",
               label=f"Target Macro F1 = {TARGET_MACRO_F1}")
    ax.set_xlabel("Clase de Retraso")
    ax.set_ylabel("F1-Score")
    ax.set_title(title)
    ax.legend()
    ax.set_ylim(0, 1.05)
    plt.xticks(rotation=45, ha="right")
    
    for bar, score in zip(bars, f1_scores):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{score:.3f}", ha="center", va="bottom", fontsize=9)
    
    plt.tight_layout()
    
    if save_path:
        from pathlib import Path
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    
    plt.show()
    return fig

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
