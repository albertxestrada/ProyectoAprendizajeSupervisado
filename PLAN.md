# Plan de acción · Anticipando el caos aéreo

Proyecto de Aprendizaje automático (520291, MUCSI Deusto).

Este plan amplía el README del repositorio y el documento «Reunión de equipo». No reemplaza al README: lo concreta. Cada tarea dice qué hacer, por qué, cuándo está terminada y qué archivo deja. Las razones salen de dos fuentes: las sesiones de clase y las decisiones ya razonadas en el proyecto personal de aviación. No asigna personas: el reparto lo decide el equipo.

---

## 0\. Cómo leer este plan

| Marca | Significado |
| :---- | :---- |
| **\[S04\]** | Sesión de clase que respalda la tarea (S01–S14, o el Playbook del tema 1). |
| **\[D Regresión\]** | Decisión del proyecto personal de aviación (`decisiones.md`), por el título de su entrada. |
| **\[Enunciado\]** | Requisito del enunciado oficial del proyecto. |
| **\[Reunión §n\]** | Arreglo listado en el documento de la reunión de equipo. |
| **Fuera del temario** | Técnica que no aparece en el material de clase. Se puede usar, pero hay que justificarla en la memoria y saber defenderla. Si hay una alternativa vista en clase, se prefiere esa. |
| **A confirmar** | Decisión que el equipo cierra en la reunión de equipo. El plan da la opción recomendada y qué cambia con la otra. |
| **Hecho cuando** | Criterio verificable para dar la tarea por cerrada. |
| **Deja** | Notebook, módulo o archivo que produce la tarea. |

Notebooks y módulos son los del README: `01_eda_bts`, `02_eda_weather`, `03_preprocessing`, `04_classification`, `05_regression`, `06_hierarchical_pipeline`, `07_error_analysis`. Módulos: `src/data_loading.py`, `preprocessing.py`, `feature_engineering.py`, `evaluation.py`, `utils.py`, más `config.py`.

---

## 1\. Qué le falta al plan actual

El plan del README está bien orientado: dos tareas conectadas, partición temporal, comparación con y sin probabilidades, y un test que se usa una sola vez. Le faltan cinco cosas, y este documento las cubre.

1. **La formulación previa a los datos** \[Playbook §1.1–1.2\]. Falta escribir quién usa la predicción, en qué momento y qué información está prohibida en ese momento. Sin el momento de corte escrito, la fuga no se puede auditar.  
2. **Una política de fuga verificable.** La lista negra `LEAKAGE_COLUMNS` deja pasar `AirTime`, `Cancelled`, `CancellationCode` y `Tail_Number`. Además, el clima del día del vuelo (`day0`) y los niveles de 250 hPa sin desfase son información del futuro \[Reunión §2\].  
3. **Cómo se generan las probabilidades que recibe el regresor** \[S11\]. El README exporta `predict_proba(X_val)`. Así, el regresor se entrena con probabilidades de un clasificador que ya vio esas filas. La solución de clase es la predicción fuera de pliegue (*out-of-fold*) del *stacking*.  
4. **Métricas ligadas a la decisión.** Un F1 macro ≥ 0,55 exige fijar un umbral, y ese umbral solo lo puede fijar el pasajero \[D Coste de cada error\]. Hacen falta métricas que recorran todos los umbrales, y probabilidades calibradas \[S04\].  
5. **El ciclo de vida y la reproducibilidad que pide la rúbrica** \[Enunciado\]: contrato de datos, *hashes*, manifiesto de ejecución, monitorización y mantenimiento. Pesa el 5 % y el README apenas lo toca.

Además, hay errores de código que el documento de la reunión ya lista (§1). Aquí se integran como tareas de la fase 1\.

---

## 2\. Fase 0 · Formulación

Es la ficha de definición del dataset del Playbook §1.1. Va al inicio de la memoria y del README.

| Elemento | Valor | Fuente |
| :---- | :---- | :---- |
| Decisión que apoya | El pasajero decide, antes de ir al aeropuerto, si mueve su recogida, su conexión o su agenda. | \[D T\_corte\] |
| Usuario | Pasajero de un vuelo nacional de EE. UU. sin escala. | \[D Población\] |
| Momento de corte (T\_corte) | **T−4 h** sobre la salida programada, provisional: 2 h para llegar al aeropuerto y 2 h para enterarse y actuar. | \[D T\_corte\] |
| Unidad de observación | Un vuelo sin escala programado. | \[D Clave\] |
| Clave | `Reporting_Airline`, `Flight_Number_Reporting_Airline`, `FlightDate`, `OriginAirportID`. | \[D Clave\] |
| Tarea de clasificación | Si el vuelo llegará con retraso (`ArrDelay` ≥ 15\) y, si es así, por qué causa. | \[Enunciado\], \[D Coste de cada error\] |
| Tarea de regresión | Cuántos minutos de retraso tendrá a la llegada (`ArrDelay`, con signo). **A confirmar.** | \[D Regresión\] |
| Conexión entre tareas | Las probabilidades del clasificador entran como variables del regresor. Se mide si aportan. | \[Enunciado\], \[S11\] |
| Información prohibida | Todo lo que ocurre después de T\_corte: tiempos reales de salida y llegada, `AirTime`, `TaxiOut`, `WheelsOff`, minutos por causa, cancelación y matrícula real (`Tail_Number`). | \[Playbook §1.2\], \[D T\_corte\], \[D Ventana\] |
| Vuelos cancelados | Fuera del entrenamiento y de la evaluación: es otro problema. Se quitan **después** de calcular la ventana de retrasos recientes. En producción, si el vuelo ya figura cancelado, no se predice. | \[D Cancelados\] |

**Por qué la clasificación no es una discretización trivial** \[Enunciado\]. El umbral de 15 minutos es la definición oficial de BTS (`ArrDel15`), y es el que usa el DOT para la puntualidad. La causa responde otra pregunta: no cuánto, sino por qué. Esa respuesta le dice al pasajero qué compensación puede reclamar. El enunciado pide justificar esta distinción, y conviene escribirla así.

**Criterios de éxito, ligados a la decisión** (se escriben antes de medir) \[S04 «Qué debe acompañar al resultado»\]:

- Clasificación: superar en AUC-PR al clasificador de prevalencia (Dummy), de forma estable en todos los bloques de validación.  
- Regresión: superar en MAE a la mediana del entrenamiento y a la regla «llega a su hora» (predicción 0).  
- Integración: el regresor con probabilidades mejora al regresor sin ellas en la mayoría de los bloques, no solo en promedio.  
- Equidad: los aeropuertos pequeños (FAA *small hub* y *nonhub*) no rinden peor que el resto en la misma métrica \[D Grupos\].

**Hecho cuando:** la ficha está en `README.md` y en `resources/docs/data_contract.md`. Cada fila tiene su fuente.

---

## 3\. Decisiones abiertas para la reunión de equipo

Cada bloque trae la recomendación y lo que cambia si el equipo se queda con la versión actual. El resto del plan está escrito para la recomendación, y cada fase señala qué se ajusta en la otra rama.

### 3.1 Población y periodo

- **Recomendado:** vuelos nacionales sin escala de todos los aeropuertos, del 25-ene-2024 a ene-2026.  
  - Por qué empieza el 25-ene-2024: los pronósticos archivados de Open-Meteo (*Previous Runs*) no están completos antes de esa fecha \[D Población\].  
  - Por qué todos los aeropuertos: con solo 20 *hubs* no existen los aeropuertos pequeños, y no se puede medir si se les perjudica \[D Grupos\].  
  - Por qué casi dos años: el test cae en otoño-invierno y el entrenamiento ve dos inviernos.  
  - Coste: más volumen. Se puede muestrear de forma estratificada por mes y por tamaño de aeropuerto, si la memoria RAM no alcanza.  
- **Versión actual:** 20 *hubs*, todo 2024\. Train hasta el 31-ago, validación sep–oct y test desde el 1-nov.  
  - Qué cambia: el análisis de equidad se hace entre *hubs* grandes y medianos, y se declara como limitación. Hay que excluir o marcar el \~5,5 % de filas anteriores al 25-ene, porque no tienen pronóstico archivado completo.

### 3.2 Objetivo de regresión

- **Recomendado:** `ArrDelay` en minutos, con signo \[D Regresión\].  
  - Responde a la pregunta del pasajero: a qué hora llega.  
  - `AirTime` se explica casi entero por la distancia (r ≈ 0,97), y las causas dominantes del retraso, aerolínea y avión anterior, ocurren en tierra.  
  - `ArrDelayMinutes` se descarta: convierte los adelantos en cero y le oculta información al pasajero.  
  - Riesgos: cola larga, y una meta de MAE ≤ 15 que puede no alcanzarse. El cambio respecto a la entrega intermedia se explica en la memoria.  
- **Versión actual:** `AirTime`.  
  - Qué cambia: el baseline lineal `Distance → AirTime` ya será muy bueno, y el aporte de las probabilidades será pequeño. Si se mantiene, conviene usar el residuo `AirTime − CRSElapsedTime` como objetivo, que el README ya deja como opción.

### 3.3 Clases

- **Recomendado:** seis clases: sin retraso, aerolínea (*carrier*), clima (*weather*), sistema aéreo (*NAS*), seguridad (*security*) y avión anterior (*late aircraft*).  
  - Las clases `Cancel_*` desaparecen porque los cancelados salen del problema \[D Cancelados\].  
  - Seguridad es diminuta. Hay dos salidas: fusionarla con aerolínea (fusión de niveles raros, \[S03\]) o mantenerla y reportar que no se aprende. Se decide al ver su frecuencia en el EDA.  
- **Versión actual:** ocho clases, con `Cancel_*`.  
  - Qué cambia: se usa la cancelación como etiqueta, pero `Cancelled` es fuga como variable. Habría que justificar por qué la cancelación se puede predecir a T−4 h. No hay fuente sobre qué parte de las cancelaciones se decide antes de ese momento \[D Cancelados\].

### 3.4 Métrica de clasificación

- **Recomendado** \[D Coste de cada error\], \[S04\]:  
  - La curva PR y el AUC-PR eligen el modelo y el umbral.  
  - La curva ROC compara grupos y periodos, porque no cambia con la prevalencia.  
  - El log-loss y el diagrama de fiabilidad comprueban la calibración.  
  - Se descartan como criterio F1, *accuracy* y *accuracy* balanceada: exigen un umbral fijo. Pueden aparecer en la matriz de confusión del umbral elegido, solo como descripción.  
- **Versión actual:** F1 macro ≥ 0,55.  
  - Qué cambia: hay que fijar el umbral antes de comparar modelos, y justificar ese umbral con un coste de error que el sistema no conoce.

---

## 4\. Fase 1 · Preprocesamiento

**Principio** \[Playbook\]: cada paso sigue el ciclo expectativa → diagnóstico → tratamiento, y deja una fila en el registro de decisiones (`experiment_log.md` o `decision_log.csv`). Lo determinista va antes de la partición. Todo lo que se aprende de los datos (imputación, límites de atípicos, escalado, codificación) se ajusta solo con train.

### P1 · Contrato de datos y trazabilidad

- **Qué:**  
  - Completar `data_contract.md` con los seis bloques del Playbook §1.6: identidad, propósito, esquema, calidad, servicio y evolución.  
  - Por cada fuente, registrar origen, responsable, frecuencia, zona horaria, términos de uso y momento de extracción. Para las API, también *endpoint*, parámetros y hora de la llamada \[Playbook §1.3\].  
  - Corregir «reanálisis» por **«pronóstico archivado»** en Open-Meteo: *Previous Runs* guarda lo que se pronosticó, no lo que ocurrió.  
- **Por qué:** la rúbrica evalúa trazabilidad y prevención de fugas (9 %), y el profesor debe poder acceder a los datos \[Enunciado\].  
- **Hecho cuando:** cada archivo crudo tiene SHA-256, URL y fecha en un manifiesto, y hay una copia compartible de las extracciones.  
- **Deja:** `resources/docs/data_contract.md`, `data/manifest.csv` (`utils.file_sha256`).

### P2 · Lista blanca de variables

- **Qué:** sustituir `LEAKAGE_COLUMNS` por una lista blanca `FEATURES_ALLOWED` en `config.py`. Cada variable lleva su momento de disponibilidad respecto a T\_corte (árbol del Playbook §1.2: si t ≤ T\_corte, entra en X).  
- **Por qué:** una lista negra falla en silencio cuando aparece una columna nueva. Hoy deja pasar `AirTime`, `Cancelled`, `CancellationCode` y `Tail_Number` \[Reunión §2\]. Es la ruta de fuga temporal de \[S03\].  
- **Hecho cuando:** un *test* comprueba que las columnas de X son un subconjunto de la lista blanca, y falla si entra otra.  
- **Deja:** `config.py`, `tests/test_features.py` (o una celda de aserciones en `03_preprocessing`).

### P3 · Arreglos de carga y transformación \[Reunión §1\]

| Arreglo | Dónde |
| :---- | :---- |
| `load_bts` quita columnas de fuga **antes** de construir la etiqueta: mover el filtrado de columnas a después de etiquetar. | `data_loading.py` |
| `load_open_meteo` ordena por nombres de columna antiguos. | `data_loading.py` |
| `load_iem`: errata `airpot_iata`; el bucle de «M» no alcanza las 14 columnas. | `data_loading.py` |
| `convert_crs_to_utc`: `astype(64)`; la hora 2400 se queda en el mismo día (debe pasar a las 00:00 del día siguiente); solo 20 zonas horarias; `pred_datetime_utc` frente a `prediction_time_utc`. | `preprocessing.py` |
| `build_classification_label` resta un conjunto a una lista (`TypeError`). | `preprocessing.py` |
| `split_temporal` usa `>` en vez de `>=` y pierde el 1-sep y el 1-nov. | `preprocessing.py` |
| `compute_bearing`: argumentos de `arctan2` invertidos; suma 360 a radianes. | `feature_engineering.py` |

- **Hecho cuando:** cada función tiene una prueba mínima con un caso conocido (por ejemplo, un vuelo a las 2400, o el 1-sep en validación) y el notebook `03` corre de principio a fin.

### P4 · Horas en UTC para todos los aeropuertos

- **Qué:**  
  - Conservar la hora local y la UTC con el patrón `campo_raw` / `campo_utc` \[Playbook\].  
  - Obtener la zona horaria de cada aeropuerto de la población, no solo de 20\.  
  - Tratar la hora 2400 como las 00:00 del día siguiente.  
  - Calcular `T_corte_utc = CRSDep_utc − 4 h`.  
- **Por qué:** todos los cruces con clima y con la ventana de retrasos dependen de esta hora. Un error aquí es una fuga invisible.  
- **Hecho cuando:** ningún aeropuerto queda sin zona, y una muestra de 20 vuelos revisada a mano coincide.

### P5 · Etiquetas

- **Qué:**  
  - Binaria: `retraso = ArrDelay >= 15`, igual que `ArrDel15` de BTS. El código actual usa `> 15` \[Reunión §3\].  
  - Causa: la de más minutos entre las cinco columnas de causa, solo si `retraso = 1`. Escribir una regla de desempate fija.  
  - Vuelo con retraso pero sin minutos de causa: hoy se asigna a aerolínea por defecto. Pasarlo a cuarentena y contar cuántos son, en vez de inventarle una causa \[Playbook §1.5\].  
  - Revisar el caso del código D, que hoy se manda a «sin retraso» \[Reunión §3\]. Con los cancelados fuera, debería desaparecer: comprobarlo.  
  - Regresión: `ArrDelay` (o la rama de `AirTime`, §3.2).  
- **Hecho cuando:** la suma por clase cuadra con el total de vuelos no cancelados, y la tabla de frecuencias va a la memoria.

### P6 · Ventana de retrasos recientes

- **Qué:**  
  - Para cada vuelo, el retraso de los vuelos de su aerolínea que llegan a su aeropuerto de origen en las 2 h anteriores a T\_corte.  
  - La ventana termina en el corte, nunca centrada.  
  - Los vuelos que debían llegar en la ventana y no han llegado cuentan con el retraso acumulado hasta el corte: `T_corte − llegada programada`. Nunca con su hora real de llegada.  
  - Los cancelados entran en la ventana como vuelos que no han llegado.  
  - Se calcula **antes** de quitar los cancelados.  
  - Resúmenes: mediana, proporción con retraso ≥ 15 y número de vuelos. La mediana porque es robusta ante la cola \[Playbook §2\].  
- **Por qué:** sustituye al vuelo anterior del mismo avión, que exigiría `Tail_Number`. La matrícula de BTS es la del avión que voló, no la asignada en el corte \[D Ventana\]. Contar solo los que aterrizaron dejaría fuera a los que van tarde: sesgo de supervivencia.  
- **Hecho cuando:** un *test* con un vuelo construido a mano confirma que ningún dato posterior al corte entra en la ventana.  
- **Deja:** `feature_engineering.recent_delays()`.  
- **Fuera del temario:** la idea viene de Rebollo y Balakrishnan (ICRAT 2012), que usan una ventana centrada. Aquí se adapta para que no haya fuga. Citarlo en la memoria.

### P7 · Congestión programada

- **Qué:** número de salidas y llegadas programadas en el aeropuerto en la hora del vuelo. Se cuenta con **todos** los vuelos programados, cancelados incluidos, antes de filtrar.  
- **Por qué:** el horario programado se conoce de antemano. Contar después de quitar cancelados usa la cancelación, que es fuga \[Reunión §2\].  
- **Hecho cuando:** el conteo se hace sobre el dataset sin filtrar, y lo comprueba una aserción.

### P8 · Clima: pronóstico archivado (Open-Meteo)

- **Qué:**  
  - Usar `_previous_day1`: el pronóstico emitido el día anterior. Origen a la hora de salida programada, destino a la hora de llegada programada.  
  - `day0` y los 250 hPa sin desfase salen: son fuga \[Reunión §2\].  
  - Comprobar si existen los 250 hPa con `previous_day1`. Si no, quitarlos, o pedir corridas concretas con la API *Single Runs* (`&run=`).  
- **Por qué:** a T−4 h, el pasajero solo tiene pronósticos emitidos antes del corte.  
- **Hecho cuando:** el contrato de datos dice qué corrida se usa y su antelación respecto a T\_corte.

### P9 · Clima observado (IEM ASOS/METAR)

- **Qué:**  
  - Última observación anterior a T\_corte en origen.  
  - En destino, también la última anterior a T\_corte: no la de la hora de llegada.  
  - «M» pasa a NaN, con un indicador `_was_missing` \[S03\].  
  - `skyc1` es texto: codificación ordinal CLR \< FEW \< SCT \< BKN \< OVC, o la altura de la primera capa BKN/OVC (techo de nubes).  
  - Antigüedad de la observación en minutos, como variable.  
- **Por qué:** una observación posterior al corte es fuga temporal \[S03, cuatro rutas de fuga\]. `skyc1` es ordinal, no nominal \[S03\].  
- **Hecho cuando:** ninguna observación usada tiene marca de tiempo posterior a T\_corte (aserción).

### P10 · Variables de calendario y ruta

- **Qué:**  
  - Hora programada (UTC y local) codificada de forma cíclica con seno y coseno; día de la semana; mes; festivo \[S03\].  
  - Distancia y rumbo (`compute_bearing` corregido).  
  - Aerolínea, origen y destino como nominales. Los niveles raros se agrupan en «otros», con el umbral aprendido en train \[S03\].  
  - Tamaño FAA del aeropuerto de origen, para equidad y también como variable.  
- **Por qué:** los códigos enteros (`OriginAirportID`) son nominales aunque se guarden como números \[Playbook §2\].  
- **Fuera del temario, opcional:** codificación por objetivo (*target encoding*) para origen y destino. Clase la ve \[S03\], pero exige hacerla fuera de pliegue: «la fila participa en su propio valor».

### P11 · EDA guiado por preguntas \[S02, Playbook §2\]

- **Qué:**  
  - Perfilado mínimo: forma, tipos, `nunique`, ausentes por columna, fila, fuente y **tiempo**, y cuantiles.  
  - Prevalencia de retraso por mes. Se predijo entre el 20 % y el 30 % \[D Coste de cada error\]: escribir el resultado junto a la predicción.  
  - Frecuencia de cada causa: decide si seguridad se fusiona (§3.3).  
  - Cobertura por tamaño de aeropuerto, y ausentes de Open-Meteo antes del 25-ene-2024.  
  - Distribución de `ArrDelay`: cola, adelantos y atípicos. Se diagnostican, no se recortan sin razón.  
  - Correlaciones solo entre numéricas. Correlacionar con la clase codificada como número no tiene sentido.  
- **Hecho cuando:** cada gráfico responde una pregunta escrita encima, y cada hallazgo deja una fila en el registro.  
- **Deja:** `01_eda_bts`, `02_eda_weather`.

### P12 · Partición temporal con separación \[S04, S07\]

- **Qué (rama recomendada):**

| Conjunto | Periodo | Uso |
| :---- | :---- | :---- |
| Desarrollo · train | 25-ene-2024 → 31-ago-2025 | Ajuste. Validación cruzada temporal dentro. |
| Desarrollo · validación | 1-sep-2025 → 31-oct-2025 | Umbral, calibración y comparación final entre candidatos. |
| Test | 1-nov-2025 → 31-ene-2026 | Una sola vez, al final. Simula el periodo de uso más reciente \[S04\]. |

- La validación cruzada dentro de train usa ventanas que avanzan (*expanding window*) por bloques de meses \[S04 «Ventanas que avanzan»\]. Por ejemplo, cuatro bloques: hasta el mes k se entrena y el mes k+1 se valida. El test queda fuera de todas las iteraciones.  
- **Separación entre conjuntos** \[S04 «Separación según disponibilidad»\]: al menos un día entre bloques, para que ninguna ventana de retrasos recientes cruce de un conjunto a otro.  
  - El hueco real de operación es mayor: BTS publica cada mes con retraso (a comprobar cuánto). Se discute en ciclo de vida (I6).  
- **Rama actual** (20 *hubs*, 2024): train hasta el 31-ago, validación sep–oct y test desde el 1-nov, ahora con `>=`. Validación cruzada con bloques mensuales de feb a ago.  
- **Por qué no `TimeSeriesSplit`:** es solo el nombre de una clase de scikit-learn. Lo que clase enseña es la idea: ventanas que avanzan con separación. Se puede usar esa clase si se le pasa `gap`, pero lo que hay que defender es el diseño.  
- **Hecho cuando:** una tabla de la memoria muestra fechas, filas y prevalencia de cada bloque.

### P13 · Transformaciones dentro de un `Pipeline`

- **Qué:** imputación, escalado y codificación dentro de un `ColumnTransformer` \+ `Pipeline` de scikit-learn, ajustado solo con train y aplicado a validación y test (`fitted_on_split="train"`).  
- **Por qué:** es la ruta de fuga por transformación \[S03\]. En la validación cruzada, los escaladores se recalculan dentro de cada entrenamiento \[S06 «Separación experimental»\].  
- **Hecho cuando:** el `Pipeline` serializado se carga en el notebook `06` sin reajustarse.  
- **Deja:** `preprocessing.build_pipeline()`, `models/preprocessor.joblib`.

### P14 · Calidad y congelación de datos

- **Qué:**  
  - Tabla de calidad (*scorecard*) con reglas CRITICAL y WARNING, y decisión por lote: ACEPTAR, NOTIFICAR o CUARENTENA \[Playbook §1.5\].  
  - Informe de calidad con las ocho dimensiones del Playbook §1.4. Representatividad y cobertura son las que más importan aquí.  
  - Congelar: guardar train, validación y test en Parquet con su *hash* y fecha. Desde ese momento nadie toca los datos sin una fila nueva en el registro.  
- **Hecho cuando:** existen `data/processed/*.parquet`, `quality_report.md` y un manifiesto de ejecución con *hashes* \[Playbook\].

---

## 5\. Fase 2 · Clasificación

**Diseño:** un clasificador multiclase de seis clases. De él sale la probabilidad binaria que necesita el pasajero: `P(retraso) = 1 − P(sin retraso)`. El umbral y la equidad se evalúan sobre esa binaria. La causa se evalúa por clase, uno contra el resto.

### C1 · Baselines \[S05\]

- **Qué:**  
  - `DummyClassifier(strategy="prior")`: el AUC-PR de referencia es la prevalencia \[S04\].  
  - Regla simple: «se retrasa si la ventana de retrasos recientes tiene mediana ≥ 15». Es la referencia de regla sencilla que pide \[S04\].  
  - Regresión logística multinomial con variables escaladas y `class_weight="balanced"`. Sin `multi_class=…`: ese argumento está obsoleto desde scikit-learn 1.5.  
- **Hecho cuando:** los tres tienen AUC-PR, log-loss y ROC en validación cruzada y en validación.

### C2 · Modelos candidatos \[S08–S11\]

| Modelo | Sesión | Hiperparámetros a explorar |
| :---- | :---- | :---- |
| KNN (opcional) | S08 | K, distancia, escalado. Probabilidades poco calibradas: comprobarlas. |
| Naive Bayes (opcional) | S08 | Suavizado. Sirve de referencia rápida. |
| Árbol de decisión | S09 | Profundidad, hojas mínimas, Gini o entropía, poda. |
| Random Forest | S10 | `n_estimators`, `max_features`, profundidad, tamaño de hoja. Error OOB. |
| Gradient Boosting / LightGBM | S11 | Tasa de aprendizaje, número de árboles con parada temprana \[S06\], hojas, `subsample` con `subsample_freq > 0`. |

- **Desbalance:** pesos de clase. En LightGBM multiclase, `is_unbalance` no hace nada: usar `class_weight="balanced"` \[Reunión §3\].  
- **No usar SMOTE ni submuestreo como opción principal.** Están fuera del temario y distorsionan las probabilidades que recibe el regresor y que lee el pasajero. Si se prueban, es solo como comparación, y recalibrando después.  
- **Hecho cuando:** cada candidato tiene su fila en el registro de experimentos con métrica, desviación entre bloques y tiempo de entrenamiento.

### C3 · Optimización de hiperparámetros \[S07\]

- **Qué:**  
  - Búsqueda aleatoria o *successive halving*, con escala logarítmica para tasas y regularización.  
  - Cada configuración pasa por los mismos bloques temporales de P12, con las transformaciones aprendidas dentro de cada bloque.  
  - Criterio: AUC-PR de la binaria. Desempate: log-loss.  
  - Comparar los dos mejores candidatos bloque a bloque (diferencia Δk por bloque) \[S07\]. No elegir por un promedio que esconde un bloque malo.  
- **Por qué:** «buscar también puede sobreajustar a la validación» \[S07\]. La validación de sep–oct no se usa para buscar, solo para confirmar.  
- **Hecho cuando:** se reporta magnitud, estabilidad y coste de cada configuración final \[S07\].

### C4 · Diagnóstico de capacidad \[S06\]

- **Qué:** brecha entre train y validación por modelo; curva de aprendizaje con fracciones crecientes de train para el mejor modelo.  
- **Por qué:** dice si conviene más datos (rama de población completa) o más capacidad \[S06 «Más datos pueden revelar qué limita el aprendizaje»\].  
- **Hecho cuando:** hay una figura y una frase de interpretación en la memoria.

### C5 · Calibración y umbral \[S04\]

- **Qué:**  
  - Diagrama de fiabilidad, Brier y log-loss de la binaria en validación.  
  - Si está mal calibrada, recalibrar con un subconjunto de desarrollo que el modelo no vio. La técnica concreta (isotónica o Platt) está **fuera del temario**: justificarla, o reportar la descalibración como limitación.  
  - Umbral: el sistema entrega la probabilidad, y el pasajero elige \[D Coste de cada error\]. Para la memoria y la demo, mostrar tres puntos de operación sobre la curva PR. Por ejemplo, precisión de 0,5, 0,6 y 0,7, con su recall.  
  - Comprobar que la proporción de vuelos predichos con retraso queda cerca de la prevalencia real (20–30 %).  
- **Hecho cuando:** la figura PR con los tres puntos y la de fiabilidad están en `04_classification`.

### C6 · Evaluación de la causa

- **Qué:** AUC-PR uno contra el resto por causa, y su media macro; matriz de confusión entre causas, solo en vuelos retrasados.  
- **Por qué:** la media macro no deja que las clases grandes tapen a las pequeñas \[S04 micro/macro/ponderada\].  
- **Hecho cuando:** hay una tabla por clase con soporte. Las clases que no se aprenden se dicen claramente.

### C7 · Probabilidades fuera de pliegue para el regresor \[S11 Stacking\]

- **Qué:**  
  - Dividir train en bloques temporales (los mismos de P12).  
  - Para cada bloque k, entrenar el clasificador final con los bloques anteriores y predecir el bloque k.  
  - El primer bloque no tiene probabilidades y queda fuera del entrenamiento del regresor: es el coste.  
  - Validación: la predice el clasificador entrenado con todo train.  
  - Test: lo predice el clasificador reentrenado con todo desarrollo (train \+ validación).  
  - Unir por la clave del vuelo, nunca por posición.  
- **Por qué:** es lo que clase llama «entrenar K versiones de cada base» para construir la matriz Z del *stacking* \[S11\]. Si el regresor aprende con `predict_proba(X_train)`, recibe probabilidades demasiado seguras, y en test se encuentra otras \[Reunión §2\]. Aquí solo se usan bloques anteriores, no todos los demás: así ningún bloque se predice con un modelo que vio el futuro.  
- **Hecho cuando:** `data/processed/oof_probs.parquet` tiene la clave, seis probabilidades por vuelo y el bloque que las generó. Una aserción comprueba que ningún vuelo se predijo con un modelo que lo vio.  
- **Deja:** `04_classification` (sección final), `src/evaluation.oof_predict()`.

---

## 6\. Fase 3 · Regresión

Escrita para `ArrDelay`. La rama de `AirTime` se indica en cada tarea.

### R1 · Baselines \[S05\]

- **Qué:**  
  - Constante 0: «llega a su hora».  
  - Mediana de train: el óptimo para el error absoluto.  
  - Media de train: el óptimo para el error cuadrático.  
  - Regla simple: la mediana de la ventana de retrasos recientes.  
  - Rama `AirTime`: regresión lineal `Distance → AirTime`.  
- **Hecho cuando:** los cuatro tienen MAE, RMSE y R² por bloque.

### R2 · Modelos \[S05, S06, S09–S11\]

| Modelo | Sesión | Nota |
| :---- | :---- | :---- |
| Regresión lineal | S05 | One-hot con categoría de referencia; revisar colinealidad. |
| Ridge, Lasso, Elastic Net | S06 | Con escalado. Lasso informa qué variables sobran. |
| Árbol de regresión | S09 | Profundidad y hojas mínimas. |
| Random Forest | S10 | Robusto ante atípicos en las variables. |
| Gradient Boosting / LightGBM | S11 | Parada temprana con validación interna \[S06\]. |
| SVR (opcional) | S09 | Probablemente caro con este volumen: descartar si no escala. |

- **Hecho cuando:** cada uno pasa por la misma búsqueda y los mismos bloques que en C3.

### R3 · Métricas y cola larga

- **Qué:**  
  - Métrica principal: **MAE**, en minutos e interpretable por el pasajero. Secundarias: RMSE, que castiga la cola, y R².  
  - MAPE no se usa: `ArrDelay` vale 0 o es negativo en muchos vuelos \[S04, cuidado con MAPE\].  
  - MAE por tramos de retraso real: adelantado, de 0 a 15, de 15 a 60, de 60 a 180 y más de 180\. Ahí se ve dónde falla.  
  - Variante opcional de \[S03\] (log1p para colas largas): como `ArrDelay` tiene negativos, usar `signo(y)·log1p(|y|)`, y volver a minutos para medir. Justificarla, porque no es la forma vista en clase.  
  - La meta de MAE ≤ 15 del README pasa a ser relativa: mejora sobre la mediana de train. Antes de medir, escribir qué mejora se espera, igual que se hizo con la prevalencia \[D Coste de cada error\].  
- **Por qué:** optimizar un número sin la pregunta detrás lleva a modelos que mejoran la métrica y no el uso.  
- **Hecho cuando:** la tabla de tramos está en `05_regression`.

### R4 · Residuos y capacidad \[S05, S06\]

- **Qué:** residuos frente a predicción, frente a hora del día y frente a tamaño de aeropuerto; brecha entre train y validación; curva de aprendizaje.  
- **Hecho cuando:** cada patrón visible tiene una frase de interpretación.

---

## 7\. Fase 4 · Integración

### I1 · Regresor con y sin probabilidades

- **Qué:**  
  - El mismo modelo y la misma búsqueda, con dos conjuntos de variables: sin probabilidades y con las seis probabilidades fuera de pliegue de C7.  
  - Comparación pareada por bloque (Δk) \[S07\]: cuántos bloques mejora, la mejora media y su dispersión.  
  - Una tercera variante, opcional: solo `P(retraso)` en lugar de las seis. Aclara si aporta la causa o solo el retraso.  
- **Por qué:** es la conexión entre tareas que pide el enunciado, y es lo que **nunca se recorta**.  
- **Hecho cuando:** hay una tabla con Δk por bloque y una conclusión que se puede defender aunque la mejora sea nula.  
- **Deja:** `06_hierarchical_pipeline`.

### I2 · Selección final y test único \[S07\]

- **Qué:**  
  1. Elegir clasificador y regresor con validación cruzada y confirmar en validación.  
  2. Reentrenar ambos con todo desarrollo (train \+ validación).  
  3. Generar las probabilidades del test con el clasificador reentrenado.  
  4. Evaluar el test **una sola vez** y anotar fecha y *hash* del modelo.  
- **Por qué:** es la ruta válida de \[S07\]. Si el test se usa para decidir, deja de medir generalización.  
- **Hecho cuando:** el resultado de test está en el registro con la versión del código y de los datos.

### I3 · Análisis de errores por grupos

- **Qué:**  
  - Por tamaño de aeropuerto (FAA), mes y estación, aerolínea y hora del día.  
  - Clasificación: ROC por grupo y periodo; recall al umbral de demo por grupo \[D Coste de cada error\], \[D Grupos\].  
  - Regresión: MAE por grupo.  
  - Un grupo sale perjudicado si su métrica es peor que la del resto en la misma métrica. La diferencia aceptable no está fijada: decirlo como limitación.  
  - Revisar los diez peores errores del test a mano y clasificarlos (clima extremo, dato ausente, avión anterior, etc.).  
- **Hecho cuando:** la tabla y el análisis de casos están en `07_error_analysis`.

### I4 · Interpretación

- **Qué:** coeficientes de la logística y de Ridge \[S05\]; importancia por impureza en el bosque \[S10\], con su límite: «la importancia no explica causalidad» y favorece variables con muchos cortes.  
- **Fuera del temario:** SHAP no aparece en el material de clase. Si se usa, justificarlo y saber explicarlo en la defensa. Si no, basta con lo de clase.

### I5 · Propuesta de uso

- **Qué:**  
  - Una función `predict_flight(clave)` que, a T\_corte, devuelve un JSON con: `P(retraso)`, la causa más probable con su probabilidad, minutos estimados de retraso y la hora estimada de llegada.  
  - Si el vuelo ya figura cancelado, la predicción vuelve vacía con un aviso \[D Cancelados\].  
  - No hace falta una API desplegada: basta la función y un ejemplo ejecutado en el notebook.  
- **Hecho cuando:** el ejemplo corre sobre tres vuelos del test (uno puntual, uno retrasado y uno de aeropuerto pequeño).

### I6 · Ciclo de vida \[rúbrica 5 %\]

- **Qué** (en la memoria, una página):  
  - Operación: a qué hora se ejecuta y qué fuentes consulta en ese momento.  
  - Monitorización: prevalencia predicha frente a real cada mes; deriva de las variables principales; calibración mensual.  
  - Mantenimiento: reentrenamiento mensual con el retraso de publicación de BTS como separación real; disparadores (la calibración sale de rango, cambia la prevalencia o entra una aerolínea nueva).  
  - Riesgos: dependencia de Open-Meteo y de IEM, cambios de códigos de aeropuerto, uso por un pasajero que confunde probabilidad con certeza.

### I7 · Reproducibilidad \[Enunciado\]

- **Qué:**  
  - Semillas fijas (`utils.set_seed`), dependencias con versión fijada en `requirements.txt`.  
  - `README.md` como punto de entrada: estructura, entorno, acceso a datos, orden de ejecución, cómo reproducir y dónde están modelos, métricas y figuras.  
  - Notebooks guardados con sus salidas. Hoy el `04` no está ejecutado \[Reunión §3\].  
  - ZIP sin entornos virtuales, cachés ni duplicados.  
- **Hecho cuando:** alguien del equipo, en una carpeta limpia, sigue el README y obtiene las mismas métricas.

---

## 8\. Fase 5 · Entrega

### E1 · Memoria (16 páginas de contenido, 20 en total)

| Sección del enunciado | Páginas | Sale de |
| :---- | :---- | :---- |
| Problema y uso | 1,5 | Fase 0 |
| Datos, análisis, calidad y preparación | 3 | P1–P14 |
| Diseño experimental | 1,5 | P12, C3 |
| Clasificación | 2 | C1–C7 |
| Regresión | 2 | R1–R4 |
| Resultados y selección (incluye integración) | 2 | I1–I3 |
| Propuesta de uso | 1 | I5 |
| Limitaciones y riesgos | 1 | I3, I6, fuera del temario |
| Reproducibilidad y ciclo de vida | 1 | I6, I7 |
| Conclusiones | 1 | — |

- Explicar el cambio de objetivo respecto a la entrega intermedia, si se adopta `ArrDelay`.  
- Todo lo marcado «fuera del temario» se justifica en una frase con su fuente.

### E2 · Defensa (10 diapositivas, 10 minutos)

- Una idea por diapositiva: problema; datos y corte; fuga y cómo se evitó; partición; clasificación; regresión; integración (con y sin); errores por grupo; uso y ciclo de vida; conclusiones.  
- Todos participan con contenido sustantivo \[Enunciado\]. Cada integrante debe poder explicar cualquier diapositiva: el contenido generado con IA que el equipo no sepa explicar penaliza la nota.

### E3 · ZIP

- Estructura del README, notebooks ejecutados, `src/`, `config.py`, `requirements.txt`, manifiesto de datos y enlace a la copia compartida de los datos.

---

## 9\. Prioridades si falta tiempo

**Orden de recorte** (de lo primero que se suelta a lo último):

1. KNN, Naive Bayes y SVR opcionales.  
2. Búsqueda de hiperparámetros del boosting: se queda con valores por defecto y parada temprana.  
3. El boosting entero.  
4. La variante logarítmica del objetivo y la recalibración.  
5. **Nunca se recorta:** la comparación con y sin probabilidades, el test único y las aserciones de fuga.

---

## 10\. Mapa de la rúbrica

| Criterio | Peso | Tareas que lo alimentan |
| :---- | :---- | :---- |
| Alineación y utilidad | 8 % | Fase 0, I5, E1 (problema y uso) |
| Datos y preprocesamiento, incluida la prevención de fugas | 9 % | P1–P14 |
| Soluciones predictivas: comparación, optimización y selección razonada | 9 % | C1–C3, R1–R2, I1–I2 |
| Diseño experimental y evaluación: validación, métricas, generalización y estudio de errores | 9 % | P12, C4–C6, R3–R4, I3 |
| Ingeniería, reproducibilidad y ciclo de vida | 5 % | C7, I6, I7, E3 |
| Calidad de la memoria y de la entrega técnica | 5 % | E1, E3 |
| Defensa | 5 % | E2 |

---

## 11\. Fuera del temario: qué se usa y cómo se justifica

| Técnica | Situación | Recomendación |
| :---- | :---- | :---- |
| SMOTE, submuestreo | No aparecen en clase. | No usarlos como principal: distorsionan las probabilidades. Pesos de clase en su lugar. |
| `TimeSeriesSplit` | La clase no aparece; la idea sí \[S04\]. | Defender el diseño de ventanas con separación, no el nombre de la clase. |
| Calibración isotónica o Platt | Clase enseña a medir la calibración \[S04\], no a corregirla. | Medir siempre. Corregir solo si hace falta, y justificarlo. |
| SHAP | No aparece en clase. | Opcional. Basta con coeficientes e importancias \[S05, S10\]. |
| Huber, regresión por cuantiles | No aparecen. | No usarlos. MAE y análisis por tramos cubren la cola. |
| Ventana de retrasos recientes | Literatura (Rebollo y Balakrishnan, 2012). | Citarla y explicar por qué aquí no va centrada. |
| Variante `signo·log1p` | log1p sí está \[S03\]; la variante con signo, no. | Opcional; explicar por qué hace falta con negativos. |

---

## 12\. Riesgos principales

| Riesgo | Señal | Respuesta |
| :---- | :---- | :---- |
| Fuga que sobrevive a los arreglos | AUC-PR sospechosamente alto (por ejemplo, \> 0,9) en validación. | Revisar la lista blanca y las marcas de tiempo; quitar variables de una en una. |
| Volumen inmanejable con todos los aeropuertos | Notebook que no cabe en memoria. | Muestreo estratificado por mes y por tamaño de aeropuerto; documentarlo. |
| Las probabilidades no aportan al regresor | Δk ≈ 0 en todos los bloques. | Es un resultado válido: reportarlo y explicar por qué (la ventana de retrasos ya lleva esa información). |
| El test de otoño-invierno difiere del entrenamiento | Prevalencia de test muy distinta a la de train. | ROC por periodo, porque no cambia con la prevalencia; discutirlo en limitaciones. |
| Seguridad no se aprende | Soporte de decenas de vuelos. | Fusionarla o reportarla como no aprendible (§3.3). |
| Retraso en los arreglos de la fase 1 | La fase 2 está por empezar y los datos aún no están congelados. | Recortar según §9; nunca empezar los modelos con datos sin congelar. |

