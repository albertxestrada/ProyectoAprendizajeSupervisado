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

---

*Ultima actualizacion: PENDIENTE*
