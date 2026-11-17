# Data Contract — Anticipando el Caos Aéreo

> Documento de trazabilidad para garantizar reproducibilidad del pipeline de datos.

## Fuentes de Datos

### 1. BTS On-Time Performance (T_ONTIME_REPORTING)

| Campo | Valor |
|---|---|
| **Proveedor** | Bureau of Transportation Statistics (BTS) |
| **URL** | https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoession_VQ=FGJ |
| **Periodo** | Enero 2024 — Diciembre 2024 |
| **Granularidad** | 1 archivo CSV por mes |
| **Registros aprox.** | ~1,490,000 vuelos domesticos |
| **Fecha de extraccion** | `PENDIENTE — Registrar al descargar` |
| **Formato** | CSV (separado por coma) |
| **Encoding** | UTF-8 |

**Campos seleccionados (pre-leakage removal):**
FlightDate, Reporting_Airline, Origin, Dest, CRSDepTime, CRSArrTime, CRSElapsedTime,
DepDelay, ArrDelay, AirTime, Distance, CarrierDelay, WeatherDelay, NASDelay,
SecurityDelay, LateAircraftDelay, Cancelled, CancellationCode, Diverted,
Marketing_Airline_Network, OriginCityName, DestCityName, OriginState, DestState

**Hashes SHA-256:**

| Archivo | SHA-256 |
|---|---|
| `bts/on_time_2024_01.csv` | `PENDIENTE` |
| `bts/on_time_2024_02.csv` | `PENDIENTE` |
| `bts/on_time_2024_03.csv` | `PENDIENTE` |
| `bts/on_time_2024_04.csv` | `PENDIENTE` |
| `bts/on_time_2024_05.csv` | `PENDIENTE` |
| `bts/on_time_2024_06.csv` | `PENDIENTE` |
| `bts/on_time_2024_07.csv` | `PENDIENTE` |
| `bts/on_time_2024_08.csv` | `PENDIENTE` |
| `bts/on_time_2024_09.csv` | `PENDIENTE` |
| `bts/on_time_2024_10.csv` | `PENDIENTE` |
| `bts/on_time_2024_11.csv` | `PENDIENTE` |
| `bts/on_time_2024_12.csv` | `PENDIENTE` |

---

### 2. Open-Meteo Previous Runs API (Jet Stream 250 hPa)

| Campo | Valor |
|---|---|
| **Proveedor** | Open-Meteo (open-source weather API) |
| **API** | Previous Runs API (datos reanálisis) |
| **Variable** | `wind_speed_250hPa`, `wind_direction_250hPa` |
| **Nivel de presion** | 250 hPa (~10,000 m / FL340) |
| **Periodo** | Enero 2024 — Diciembre 2024 |
| **Granularidad temporal** | Horaria |
| **Coordenadas** | 20 Core Hubs FAA (ver lista abajo) |
| **Fecha de extraccion** | `PENDIENTE — Registrar al descargar` |
| **Formato** | JSON / CSV |

**Estadisticas esperadas (jet stream):**
- Media: ~57 kt
- Picos: hasta ~213 kt
- Componente headwind/tailwind significativa para AirTime

**Hashes SHA-256:**

| Archivo | SHA-256 |
|---|---|
| `open_meteo/wind_250hPa_2024.csv` | `PENDIENTE` |

---

### 3. IEM ASOS/METAR (Ceiling & Visibility)

| Campo | Valor |
|---|---|
| **Proveedor** | Iowa Environmental Mesonet (IEM) |
| **URL** | https://mesonet.agron.iastate.edu/request/download.phtml |
| **Estaciones** | ASOS/METAR en 20 Core Hubs FAA |
| **Variables** | `skyc1` (ceiling), `vsby` (visibility en millas) |
| **Periodo** | Enero 2024 — Diciembre 2024 |
| **Granularidad temporal** | Observaciones (~cada 20-60 min) |
| **Fecha de extraccion** | `PENDIENTE — Registrar al descargar` |
| **Formato** | CSV |
| **Sentinels** | "M" = Missing → NaN |

**Hashes SHA-256:**

| Archivo | SHA-256 |
|---|---|
| `iem/asos_metar_2024.csv` | `PENDIENTE` |

---

## 20 Core Hubs FAA

| # | IATA | Nombre | Timezone (IANA) |
|---|---|---|---|
| 1 | ATL | Atlanta Hartsfield-Jackson | America/New_York |
| 2 | DFW | Dallas/Fort Worth | America/Chicago |
| 3 | DEN | Denver International | America/Denver |
| 4 | ORD | Chicago O'Hare | America/Chicago |
| 5 | LAX | Los Angeles International | America/Los_Angeles |
| 6 | CLT | Charlotte Douglas | America/New_York |
| 7 | MCO | Orlando International | America/New_York |
| 8 | LAS | Las Vegas McCarran | America/Los_Angeles |
| 9 | PHX | Phoenix Sky Harbor | America/Phoenix |
| 10 | MIA | Miami International | America/New_York |
| 11 | SEA | Seattle-Tacoma | America/Los_Angeles |
| 12 | IAH | Houston Bush | America/Chicago |
| 13 | JFK | New York JFK | America/New_York |
| 14 | EWR | Newark Liberty | America/New_York |
| 15 | SFO | San Francisco International | America/Los_Angeles |
| 16 | MSP | Minneapolis-St. Paul | America/Chicago |
| 17 | BOS | Boston Logan | America/New_York |
| 18 | DTW | Detroit Metropolitan | America/New_York |
| 19 | FLL | Fort Lauderdale-Hollywood | America/New_York |
| 20 | PHL | Philadelphia International | America/New_York |

---

## Reglas de Reproducibilidad

1. **RANDOM_STATE = 42** en todo el pipeline
2. **Split temporal** (sin shuffle): Train ene-ago, Val sep-oct, Test nov-dic 2024
3. Los hashes SHA-256 se calculan con `src/utils.py::file_sha256()` al momento de descarga
4. Registrar fecha exacta de cada descarga en este documento
5. Las 22 columnas de leakage se eliminan ANTES de cualquier modelado (ver `config.py::LEAKAGE_COLUMNS`)

---

## Instrucciones para Registrar Hashes

```python
from src.utils import file_sha256

# Ejemplo: registrar hash de un archivo BTS
hash_val = file_sha256("data/raw/bts/on_time_2024_01.csv")
print(f"SHA-256: {hash_val}")
# Copiar el hash a la tabla correspondiente en este documento
```

---

*Ultima actualizacion: PENDIENTE*
