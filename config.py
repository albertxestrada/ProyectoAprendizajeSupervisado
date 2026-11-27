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
# Lista blanca de variables disponibles antes de T-4 h
# La lista solo contiene identificadores y datos conocidos al corte.
# Las etiquetas y resultados operativos nunca deben pasar a FEATURES_ALLOWED.
# =============================================================================
FEATURES_ALLOWED = {
    # Identidad temporal y aerolinea
    "Year",
    "Quarter",
    "Month",
    "DayofMonth",
    "DayOfWeek",
    "FlightDate",
    "Reporting_Airline",
    "DOT_ID_Reporting_Airline",
    "IATA_CODE_Reporting_Airline",
    "Flight_Number_Reporting_Airline",
    # Ruta y programacion
    "OriginAirportID",
    "Origin",
    "OriginCityName",
    "OriginState",
    "DestAirportID",
    "Dest",
    "DestCityName",
    "DestState",
    "CRSDepTime",
    "CRSArrTime",
    "CRSElapsedTime",
    "DepTimeBlk",
    "ArrTimeBlk",
    "Distance",
    "DistanceGroup",
    "Flights",
    # Horas normalizadas
    "dep_datetime_utc",
    "arr_datetime_utc",
    "prediction_time_utc",
    "pred_datetime_utc",
    "T_corte_utc",
    # Clima disponible al corte
    "timestamp_utc",
    "time",
    "station",
    "wind_speed_250hPa",
    "wind_direction_250hPa",
    "wind_speed_10m",
    "wind_direction_10m",
    "skyc1",
    "vsby",
    # Features derivadas
    "flight_bearing",
    "headwind_component",
    "crosswind_component",
    "hour_sin",
    "hour_cos",
    "dow_sin",
    "dow_cos",
    "is_weekend",
    "month_sin",
    "month_cos",
    "is_holiday_window",
    "origin_daily_flights",
    "origin_scheduled_departures_hour",
    "origin_scheduled_arrivals_hour",
    "dest_scheduled_departures_hour",
    "dest_scheduled_arrivals_hour",
    "scheduled_departures_hour",
    "scheduled_arrivals_hour",
    "origin_hour_congestion",
    "dest_hour_congestion",
    "recent_delay_median",
    "recent_delay_rate",
    "recent_flight_count",
}

# Compatibilidad temporal durante P2. El nuevo pipeline debe usar
# FEATURES_ALLOWED; LEAKAGE_COLUMNS no debe ampliarse ni usarse para modelado.
LEAKAGE_COLUMNS = [
    "DepTime", "DepDelay", "DepDelayMinutes", "DepDel15",
    "DepartureDelayGroups", "TaxiOut", "WheelsOff",
    "WheelsOn", "TaxiIn", "ArrTime", "ArrDelay",
    "ArrDelayMinutes", "ArrDel15", "ArrivalDelayGroups",
    "ActualElapsedTime", "Diverted", "DivAirportLandings",
    "CarrierDelay", "WeatherDelay", "NASDelay",
    "SecurityDelay", "LateAircraftDelay",
    "Cancelled", "CancellationCode", "Tail_Number",
]

# =============================================================================
# Target de regresion
# =============================================================================
REGRESSION_TARGET = "ArrDelay"

# =============================================================================
# Etiquetas de clasificacion multiclase
# Construidas combinando causas de demora con CancellationCode
# =============================================================================
CLASSIFICATION_LABELS = [
    "OnTime",
    "Delay_Carrier",
    "Delay_Weather",
    "Delay_NAS",
    "Delay_Security",
    "Delay_LateAircraft",
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

# Periodo de datos del proyecto
DATA_START = "2024-02-01"
DATA_END = "2025-12-31"