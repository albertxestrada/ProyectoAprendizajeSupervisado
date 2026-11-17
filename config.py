"""
Configuracion centralizada del proyecto.
Todas las constantes, semillas, rutas y fechas de split se definen aqui.
Importar desde este archivo en notebooks y modulos de src/.
"""

from pathlib import Path

# =============================================================================
# Rutas del proyecto
# =============================================================================
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
SPLITS_DIR = PROCESSED_DIR / "splits"
MODELS_DIR = PROJECT_ROOT / "models"
RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = RESULTS_DIR / "figures"
TABLES_DIR = RESULTS_DIR / "tables"

# =============================================================================
# Reproducibilidad
# =============================================================================
RANDOM_STATE = 42

# =============================================================================
# Separacion temporal (cronologica, sin fugas)
# Basado en vuelos domesticos EE.UU. 2024
# =============================================================================
TRAIN_END = "2024-08-31"      # Train: Ene-Ago 2024
VAL_START = "2024-09-01"
VAL_END = "2024-10-31"        # Validation: Sep-Oct 2024
TEST_START = "2024-11-01"     # Test: Nov-Dic 2024

# =============================================================================
# Columnas excluidas por data leakage (informacion post-vuelo)
# Identificadas en la entrega intermedia
# =============================================================================
LEAKAGE_COLUMNS = [
    "DepTime", "DepDelay", "DepDelayMinutes", "DepDel15",
    "DepartureDelayGroups", "TaxiOut", "WheelsOff",
    "WheelsOn", "TaxiIn", "ArrTime", "ArrDelay",
    "ArrDelayMinutes", "ArrDel15", "ArrivalDelayGroups",
    "ActualElapsedTime", "Diverted", "DivAirportLandings",
    "CarrierDelay", "WeatherDelay", "NASDelay",
    "SecurityDelay", "LateAircraftDelay",
]

# =============================================================================
# Target de regresion
# =============================================================================
REGRESSION_TARGET = "AirTime"

# =============================================================================
# Etiquetas de clasificacion multiclase
# Construidas combinando causas de demora con CancellationCode
# =============================================================================
CLASSIFICATION_LABELS = [
    "OnTime",
    "Delay_Carrier",
    "Delay_Weather",
    "Delay_NAS",
    "Delay_LateAircraft",
    "Cancel_Carrier",
    "Cancel_Weather",
    "Cancel_NAS",
]

# =============================================================================
# Aeropuertos Core Hubs FAA (20 hubs principales)
# =============================================================================
CORE_HUBS = [
    "ATL", "DFW", "DEN", "ORD", "LAX",
    "CLT", "MCO", "LAS", "PHX", "MIA",
    "SEA", "IAH", "JFK", "EWR", "SFO",
    "MSP", "BOS", "DTW", "FLL", "PHL",
]

# =============================================================================
# Metricas objetivo
# =============================================================================
TARGET_MAE = 15        # minutos
TARGET_MACRO_F1 = 0.55

# =============================================================================
# Parametros de Open-Meteo (nivel de presion para jet stream)
# =============================================================================
PRESSURE_LEVEL_HPA = 250  # Nivel de crucero para vientos en altura
