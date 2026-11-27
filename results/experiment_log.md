# Experiment Log — Anticipando el Caos Aéreo

> Registro de todos los experimentos del proyecto. Cada fila documenta
> un run para garantizar reproducibilidad y facilitar la comparacion.

## Clasificacion (8 clases de retraso)

| # | Fecha | Modelo | Hiperparametros | Balanceo | Features | Macro F1 (val) | Accuracy (val) | Notas |
|---|---|---|---|---|---|---|---|---|
| C01 | | LogisticRegression | default | class_weight='balanced' | baseline | | | Baseline clasificacion |
| C02 | | RandomForest | n_estimators=100 | class_weight='balanced' | baseline | | | |
| C03 | | XGBoost | default | scale_pos_weight | baseline | | | |
| C04 | | LightGBM | default | is_unbalance=True | baseline | | | |
| C05 | | Mejor C01-C04 | tuned | SMOTE | + weather | | | Con features meteorologicas |
| C06 | | Mejor C01-C04 | tuned | SMOTE | + jet stream | | | Con headwind/tailwind |
| C07 | | Mejor C01-C04 | tuned | SMOTE | all features | | | Feature engineering completo |

## Regresion (AirTime en minutos)

| # | Fecha | Modelo | Hiperparametros | Features | MAE (val) | RMSE (val) | R² (val) | Notas |
|---|---|---|---|---|---|---|---|---|
| R01 | | LinearRegression | default | Distance only | | | | Baseline: Distance→AirTime (r≈0.97) |
| R02 | | RandomForest | n_estimators=100 | baseline | | | | |
| R03 | | XGBoost | default | baseline | | | | |
| R04 | | LightGBM | default | baseline | | | | |
| R05 | | Mejor R01-R04 | tuned | + classifier_proba | | | | Pipeline jerarquico |
| R06 | | Mejor R01-R04 | tuned | + jet stream | | | | Con headwind/tailwind |
| R07 | | Mejor R01-R04 | tuned | all features | | | | Feature engineering completo |

## Objetivos

| Tarea | Metrica | Objetivo |
|---|---|---|
| Clasificacion | Macro F1 | ≥ 0.55 |
| Regresion | MAE | ≤ 15 min |

## Instrucciones

1. Llenar cada fila al completar un experimento
2. Registrar hiperparametros exactos (o referir al notebook)
3. Reportar metricas sobre **validation set** (sep-oct 2024)
4. El **test set** (nov-dic 2024) se usa SOLO para la evaluacion final
5. Guardar figuras en `results/figures/` y tablas en `results/tables/`

## Trazabilidad de preprocesamiento

| # | Fecha | Fase | Cambio | Evidencia |
|---|---|---|---|---|
| P1 | 2026-11-27 | Contrato y trazabilidad | Contrato actualizado, periodo real documentado y Open-Meteo corregido como pronóstico archivado | `data/data_contract.md`; `data/manifest.csv`; 26 hashes y tamaños verificados |
| P2 | 2026-11-27 | Lista blanca de variables | Se añadió `FEATURES_ALLOWED` y `validate_features()`; las variables operativas y objetivos quedan fuera de `X` | `config.py`; `src/data_loading.py`; `tests/test_features.py` |
| P3 | 2026-11-27 | Carga y transformación | Corregidas UTC 2400, etiqueta >=15, límites temporales, carga meteorológica/IEM y bearing | `src/data_loading.py`; `src/preprocessing.py`; `src/feature_engineering.py`; `tests/test_p3_preprocessing.py` |
| P4 | 2026-11-27 | Horas UTC | Conversión por zona IANA de origen y destino, T_corte UTC y cuarentena de aeropuertos sin zona | `src/preprocessing.py`; `tests/test_p4_timezone.py` |
| P5 | 2026-11-27 | Etiquetas | ArrDelay >=15, causa dominante con desempate fijo, cuarentena de cancelados y causas ausentes, regresión con ArrDelay | `config.py`; `src/preprocessing.py`; pruebas P3/P5 |
| P6 | 2026-11-27 | Ventana de retrasos recientes | Mediana, tasa ≥15 y conteo por aerolínea/aeropuerto en 2 h antes del corte; cancelados con retraso acumulado | `src/feature_engineering.py`; `tests/test_p6_recent_delays.py` |
| P7 | 2026-11-27 | Congestión programada | Conteos UTC por hora de salidas y llegadas programadas en origen/destino, incluyendo cancelados | `src/feature_engineering.py`; `config.py`; `tests/test_p7_scheduled_congestion.py` |

---

*Última actualización P1: 2026-11-27*
