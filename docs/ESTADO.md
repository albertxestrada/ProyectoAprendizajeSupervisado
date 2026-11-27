# Estado del proyecto

Qué está hecho y qué falta en cada tarea. El [plan](PLAN.md) dice qué hacer, quién y por qué; este archivo dice solo hasta dónde se ha llegado.

**Última revisión:** `main` en `cf08ff1`, con las ramas `dylan_branch`, `camilo_branch`, `emilio_branch` y `feature/clasificacion-alberto`. Los últimos cambios de `camilo_branch` y `emilio_branch` aún no están reflejados: cada uno actualiza sus filas en su PR.

> **Dónde estamos.** La descarga y los cargadores funcionan, y los siete arreglos de la reunión están hechos. Falta casi todo lo que viene después de cargar.
>
> **Qué bloquea.** La partición de `config.py` sigue en 2024, y las horas UTC solo cubren 20 aeropuertos: el resto de vuelos se pierde sin aviso.
>
> **Qué va primero.** La base del repositorio (B1–B9) y el preprocesamiento hasta congelar los datos (P1–P14). Los modelos no arrancan con datos sin congelar.

---

## Cómo se lee y cómo se actualiza

| Marca | Significado |
|---|---|
| ● Hecho | Está en `main` y cumple el «hecho cuando» de su ficha en el plan. |
| ◐ Parcial | Existe código, pero le falta algo para cumplir el «hecho cuando». |
| ○ Pendiente | No existe todavía. |

- Quien avanza o cierra una tarea cambia su fila **en el mismo PR**. Un PR que cierra una tarea sin tocar su fila no está terminado.
- Una tarea terminada en una rama sigue en ◐ hasta llegar a `main`, y «Qué falta» lo dice.
- Cuando un hallazgo se resuelve, su fila sale de la tabla de hallazgos.
- Los estados se escriben solo aquí. El plan y el README no los repiten, para que nunca se contradigan.

---

## Tareas

Cada ID enlaza con su ficha en el plan.

### Base del repositorio

| ID | Tarea | Responsable | Estado | Qué falta |
|---|---|---|---|---|
| [B1](PLAN.md#b1--gitignore-correcto) | `.gitignore` correcto y fuera los `.DS_Store` | Emilio | ○ | Patrones mal escritos; tres `.DS_Store` versionados |
| [B2](PLAN.md#b2--importar-sin-syspath) | Importar sin `sys.path` y descubrir las pruebas | Alberto | ○ | `sys.path.append` en seis `.py` y el notebook 04; falta `tests/__init__.py` |
| [B3](PLAN.md#b3--una-sola-fuente-de-aeropuertos) | Una sola fuente de aeropuertos | Camilo | ○ | Datos de aeropuertos en cuatro sitios |
| [B4](PLAN.md#b4--constantes-en-configpy) | Constantes en `config.py` | Camilo | ○ | Horizonte de 4 h fuera de config |
| [B5](PLAN.md#b5--entorno-fijado) | Entorno fijado | Dylan | ◐ | Hecho en `dylan_branch`: Python 3.12, `uv.lock` y `requirements.txt`. Falta llegar a `main` y probarlo con el notebook 03 cuando exista |
| [B6](PLAN.md#b6--descarga-que-falla-en-voz-alta) | Descarga que falla en voz alta | Camilo | ○ | Errores tragados; nombres con `_2024` |
| [B7](PLAN.md#b7--pruebas-separadas) | Pruebas separadas por tipo | Dylan | ◐ | La de datos reales no se salta; la de partición fija 2024; la de viento no mira el signo |
| [B8](PLAN.md#b8--datos-compartidos) | Datos compartidos y verificables | Emilio | ◐ | Hashes sí; falta Release, manifiesto y script de verificación |
| [B9](PLAN.md#b9--fusionar-ramas) | Fusionar ramas pendientes | Alberto · Emilio | ○ | Una rama vieja y una con conflictos |

### Preprocesamiento

| ID | Tarea | Responsable | Estado | Qué falta |
|---|---|---|---|---|
| [P1](PLAN.md#p1--contrato-de-datos-y-trazabilidad) | Contrato de datos y trazabilidad | Emilio | ◐ | «Reanálisis»; `skyc1` como techo; recuento de filas; seis bloques del Playbook |
| [P2](PLAN.md#p2--lista-blanca-de-variables) | Lista blanca de variables | Camilo | ○ | Hoy es lista negra |
| [P3](PLAN.md#p3--arreglos-de-carga-y-transformación) | Arreglos de carga y transformación | Camilo | ◐ | Los siete arreglos de la reunión, hechos. Faltan dos restos (filtro de meses sin año y columna duplicada), las pruebas por función y el notebook 03 |
| [P4](PLAN.md#p4--horas-en-utc-para-todos-los-aeropuertos) | Horas UTC de todos los aeropuertos | Camilo | ◐ | Solo 20 zonas; filas borradas sin aviso |
| [P5](PLAN.md#p5--etiquetas) | Etiquetas | Camilo | ◐ | Código D, desviados, seguridad y retraso sin causa |
| [P6](PLAN.md#p6--ventana-de-retrasos-recientes) | Ventana de retrasos recientes | Camilo | ○ | Sin empezar |
| [P7](PLAN.md#p7--congestión-programada) | Congestión programada | Camilo | ◐ | Cuenta por día; falta asegurar que va antes de quitar cancelados |
| [P8](PLAN.md#p8--clima-pronóstico-archivado-open-meteo) | Clima: pronóstico archivado | Emilio | ◐ | `day0`; signo del viento de cara; solo origen |
| [P9](PLAN.md#p9--clima-observado-iem-asosmetar) | Clima observado | Emilio | ◐ | `skyc1` sin `skyl1`; solo origen; sin antigüedad |
| [P10](PLAN.md#p10--variables-de-calendario-y-ruta) | Calendario y ruta | Camilo | ◐ | Niveles raros y tamaño FAA |
| [P11](PLAN.md#p11--eda-guiado-por-preguntas) | EDA guiado por preguntas | Camilo (BTS) · Emilio (clima) | ○ | Notebooks 01 y 02 no existen |
| [P12](PLAN.md#p12--partición-temporal-con-separación) | Partición temporal | Camilo | ◐ | Fechas de 2024 en config |
| [P13](PLAN.md#p13--transformaciones-dentro-de-un-pipeline) | Transformaciones en un `Pipeline` | Camilo | ○ | Sin empezar |
| [P14](PLAN.md#p14--calidad-y-congelación-de-datos) | Calidad y congelación | Emilio | ◐ | `save_splits` existe; faltan reglas, informe y hashes |

### Clasificación

| ID | Tarea | Responsable | Estado | Qué falta |
|---|---|---|---|---|
| [C1](PLAN.md#c1--baselines) | Baselines | Alberto | ◐ | Notebook 04 sin ejecutar; funciones solo en su rama |
| [C2](PLAN.md#c2--modelos-candidatos) | Modelos candidatos | Alberto | ◐ | SMOTE y submuestreo; `is_unbalance` en multiclase |
| [C3](PLAN.md#c3--optimización-de-hiperparámetros) | Búsqueda de hiperparámetros | Alberto | ◐ | Comprobar separación entre bloques y criterio AUC-PR |
| [C4](PLAN.md#c4--diagnóstico-de-capacidad) | Diagnóstico de capacidad | Alberto | ○ | Sin empezar |
| [C5](PLAN.md#c5--calibración-y-umbral) | Calibración y umbral | Alberto | ○ | Sin empezar |
| [C6](PLAN.md#c6--evaluación-de-la-causa) | Evaluación de la causa | Alberto | ○ | Sin empezar |
| [C7](PLAN.md#c7--probabilidades-fuera-de-pliegue-para-el-regresor) | Probabilidades fuera de pliegue | Alberto | ○ | Hoy exporta `predict_proba` sobre validación |

**Notebook 04** (rama de Alberto): 52 celdas escritas, ninguna ejecutada. Ya trae curvas PR, `average_precision`, `Pipeline` con escalado y búsqueda con `TimeSeriesSplit`. Le sobran SMOTE, el submuestreo e `is_unbalance`, y le falta la parte fuera de pliegue.

### Regresión

| ID | Tarea | Responsable | Estado | Qué falta |
|---|---|---|---|---|
| [R1](PLAN.md#r1--baselines) | Baselines | Dylan | ○ | Sin empezar |
| [R2](PLAN.md#r2--modelos) | Modelos | Dylan | ○ | Sin empezar |
| [R3](PLAN.md#r3--métricas-y-cola-larga) | Métricas y cola larga | Dylan | ○ | Funciones de regresión vacías en `src/evaluation.py` |
| [R4](PLAN.md#r4--residuos-y-capacidad) | Residuos y capacidad | Dylan | ○ | Sin empezar |

### Integración

| ID | Tarea | Responsable | Estado | Qué falta |
|---|---|---|---|---|
| [I1](PLAN.md#i1--regresor-con-y-sin-probabilidades) | Regresor con y sin probabilidades | Dylan | ○ | Sin empezar |
| [I2](PLAN.md#i2--selección-final-y-test-único) | Selección final y test único | Emilio | ○ | Sin empezar |
| [I3](PLAN.md#i3--análisis-de-errores-por-grupos) | Errores por grupos | Emilio | ○ | Sin empezar |
| [I4](PLAN.md#i4--interpretación) | Interpretación | Alberto · Dylan | ○ | Sin empezar |
| [I5](PLAN.md#i5--propuesta-de-uso) | Propuesta de uso | Emilio | ○ | Sin empezar |
| [I6](PLAN.md#i6--ciclo-de-vida) | Ciclo de vida | Emilio | ○ | Sin empezar |
| [I7](PLAN.md#i7--reproducibilidad) | Reproducibilidad | Emilio | ◐ | Semillas sí; versiones fijadas solo en `dylan_branch` (B5); notebooks sin salidas |

### Entrega

| ID | Tarea | Responsable | Estado | Qué falta |
|---|---|---|---|---|
| [E1](PLAN.md#e1--memoria) | Memoria | Emilio | ○ | Sin empezar |
| [E2](PLAN.md#e2--defensa) | Defensa | Todos | ○ | Sin empezar |
| [E3](PLAN.md#e3--zip) | ZIP | Emilio | ○ | Sin empezar |

---

## Hallazgos abiertos

Lo que encontró la revisión del repositorio y sigue sin resolver, ordenado por tarea. Cada hallazgo se cierra con su tarea.

| Tarea | Hallazgo | Por qué importa |
|---|---|---|
| B1 | `.gitignore` con errores. | `_pycache_/` está mal escrito; `models/*/.joblib` no ignora ningún modelo; `*.csv` también ignoraría el manifiesto; los Parquet no se ignoran. |
| B1 | Tres `.DS_Store` versionados. | Ruido en cada cambio. |
| B2 | `sys.path.append` en los cinco módulos de `src/`, en `download_data.py` y en el notebook 04. | Los imports dependen de la carpeta desde la que se arranca. |
| B2 | `python -m unittest` corre cero pruebas. | Falta `tests/__init__.py`. |
| B3 | Las estructuras de aeropuertos están en cuatro sitios: `CORE_HUBS`, dos `HUB_COORDS` y `AIRPORT_TIMEZONES`, más `IATA_TO_ICAO`. | Cuatro copias acaban diciendo cosas distintas. |
| B4 | El horizonte de cuatro horas vive en `preprocessing.py`, no en `config.py`. | Cambiar el corte obliga a tocar código. |
| B6 | La descarga captura `except Exception`, sigue y termina con código 0. | Una descarga incompleta parece terminada. |
| B6 | Archivos de clima con `_2024` en el nombre. | Cubren dos años. |
| B7 | Una prueba necesita los datos reales y no se salta. | Falla en cualquier clon limpio. |
| B7 | La prueba de partición fija las fechas de 2024. | Hay que cambiarla con P12. |
| B8 | Datos de unos 5 GB. | No caben en git; necesitan Release o carpeta compartida. |
| B9 | Ramas pendientes. | `emilio_branch` choca con `main`; `feature/clasificacion-alberto` nació antes que `main` y arrastra versiones viejas de `src/`. |
| P1 | El contrato llama «reanálisis» a Open-Meteo *Previous Runs*. | Son pronósticos archivados, no un reanálisis: la memoria debe decir qué se sabía en el corte. |
| P1 | El contrato dice «~1,49 M vuelos». | La descarga trae todos los aeropuertos: una prueba exige más de 500 000 filas solo en febrero. Recontar. |
| P2 | `LEAKAGE_COLUMNS` es una lista negra. | Falla en silencio cuando aparece una columna nueva. |
| P3 | `load_bts(months=…)` filtra el mes sin mirar el año. | `months=[2]` trae febrero de 2024 y de 2025. |
| P3 | Columna duplicada `prediction_time_utc`. | Dos nombres para la misma hora. |
| P4 | `convert_crs_to_utc` solo conoce 20 zonas horarias. | El resto de vuelos queda sin hora, y el cruce de clima lo borra sin avisar (`dropna`). |
| P5 | Casos borde de la etiqueta. | El código D y los desviados caen en «sin retraso»; seguridad se ignora; un retraso sin causa va a aerolínea. |
| P7 | La congestión cuenta vuelos por día. | El plan pide por hora y antes de quitar cancelados. |
| P8 | Open-Meteo se descarga con `day0`. | Es fuga: a cuatro horas de la salida solo existen los pronósticos emitidos antes del corte. |
| P8 | Signo del viento de cara invertido. | Con la convención meteorológica, el viento de cara es `+V·cos(dir − rumbo)`; el código lleva un menos. La prueba solo comprueba que la columna existe. |
| P9 | IEM pide `skyc1`, no `skyl1`. | `skyc1` dice la cobertura, no la altura: no da el techo de nubes. |
| P11, P13, R, I | No existen los notebooks 01, 02, 03, 05, 06 ni 07. | Solo hay un 04, en la rama de Alberto. |
| P12 | La partición de `config.py` sigue en 2024. | Con datos hasta dic-2025, train queda en feb–ago 2024 (sin diciembre ni enero) y test, sin fecha de fin, en 14 meses. |
| C1, R3 | `src/evaluation.py` son plantillas vacías en `main`. | Las métricas de clasificación están solo en la rama de Alberto, y las de regresión no existen. |
| C1–C3 | El notebook 04 no está ejecutado, usa SMOTE y `is_unbalance`. | SMOTE distorsiona las probabilidades que recibe el regresor, e `is_unbalance` no hace nada en multiclase. |
