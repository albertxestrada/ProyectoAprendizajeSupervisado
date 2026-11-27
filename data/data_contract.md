# Data Contract — Anticipando el Caos Aéreo

> Documento de trazabilidad para garantizar reproducibilidad del pipeline de datos.

## Fuentes de Datos

### 1. BTS On-Time Performance (T_ONTIME_REPORTING)

| Campo | Valor |
|---|---|
| **Proveedor** | Bureau of Transportation Statistics (BTS) |
| **URL** | https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoession_VQ=FGJ |
| **Periodo** | Febrero 2024 — Diciembre 2025 |
| **Granularidad** | 1 archivo CSV por mes |
| **Registros aprox.** | ~1,490,000 vuelos domesticos |
| **Fecha de extraccion** | `2026-11-27` |
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
| `bts/on_time_2024_02.csv` | `93124efb0044290561d7b077854ab6a539590151865f6b7a433320ec652ecdbe` |
| `bts/on_time_2024_03.csv` | `921fb78d9f7e4e181ecee146dbd6dc7925ccbae53fbdc0677e1c69e820be94c1` |
| `bts/on_time_2024_04.csv` | `80f5e471ba0ad42e9ab36abc8b7bfc08ae461c339fb7bc01a638cd2bd2d49e3e` |
| `bts/on_time_2024_05.csv` | `c3d4c4287efba23bb9332aa5b2b803d59e5fda2a3983623584970f130055c277` |
| `bts/on_time_2024_06.csv` | `a96a696f4e1972a9f239ae6bf665a0af4169d6447ccdc452430c9cbf6ac406d7` |
| `bts/on_time_2024_07.csv` | `08894d7a211469ff69234ea0ba5c8bad1abe565d0bfe3f1b547798a605078173` |
| `bts/on_time_2024_08.csv` | `a154c46b18d8dad0be6bbc30d9d01c840de697650b909e563475fc3a8d622d44` |
| `bts/on_time_2024_09.csv` | `2777b29a7d63ca0664006f647068f40cc0dda2b7c8a44b4415aa9ce44109da07` |
| `bts/on_time_2024_10.csv` | `23fdedaa43330b7f96ba6be740fedbfefd581f111edc548a74fa0bdb3c140527` |
| `bts/on_time_2024_11.csv` | `8698d29045044a70986640a22a9b43e69c45eae5a6f3f8e9b70db9db3dca1c58` |
| `bts/on_time_2024_12.csv` | `7900dd58227dc71e64a0e220000240ad6292e0f8c50ba16fb627b0976ceb68af` |
| `bts/on_time_2025_01.csv` | `d7c7d59452cad1215d9605e8ff350a4bad7282750765084fe57928a5ad275453` |
| `bts/on_time_2025_02.csv` | `fd6b7aa423cfe89be9d8dfa9374ffe23e6d42ea306b710b58313dba0ca0cfa0e` |
| `bts/on_time_2025_03.csv` | `ba031a484a67f743869bc1284a09fa1de61cf35a6da010e87674a3dc128590d0` |
| `bts/on_time_2025_04.csv` | `1124d8e68633acc2aeff5e1f1994a6bdc90af18370aa0440ad8bcbd2928f3307` |
| `bts/on_time_2025_05.csv` | `644c6d36949a7d563b7dc44a3f5fe4091edfcf12384b7b1cd89324536e57f5f8` |
| `bts/on_time_2025_06.csv` | `a5b0b743e01ea5c06fe721f4435923cab6ffc400b714823b614e187a2bea833e` |
| `bts/on_time_2025_07.csv` | `8e1889b42eb9a78bad273d7bb415305e4fe86af4d154fe40203484c402081eb5` |
| `bts/on_time_2025_08.csv` | `8300437f9b545871a3914fe33e4855fa15e3237c6aa3f6996d7e3f34abe6167f` |
| `bts/on_time_2025_09.csv` | `6b189acc187fcb51deb4821f12b87ab68b43a1ea2a34e3bb073a8fd807b1120b` |
| `bts/on_time_2025_10.csv` | `1162446fa628fd43729e28f5741bd1ad5b2a8012deace8efff6595c69f1b3070` |
| `bts/on_time_2025_11.csv` | `6d6d63f3bb312a6695d4a8b17958bc47e4e71fdf7396ec882c9c9a61faa6efc2` |
| `bts/on_time_2025_12.csv` | `ed0a645562652fe2d816fbcb13ba46df6e3306344d9c4728c7ce5fe57bbd0db5` |

---

### 2. Open-Meteo Previous Runs API (Jet Stream 250 hPa)

| Campo | Valor |
|---|---|
| **Proveedor** | Open-Meteo (open-source weather API) |
| **API** | Previous Runs API (datos reanálisis) |
| **Variable** | `wind_speed_250hPa`, `wind_direction_250hPa` |
| **Nivel de presion** | 250 hPa (~10,000 m / FL340) |
| **Periodo** | Febrero 2024 — Diciembre 2025 |
| **Granularidad temporal** | Horaria |
| **Coordenadas** | 20 Core Hubs FAA (ver lista abajo) |
| **Fecha de extraccion** | `2026-11-27` |
| **Formato** | JSON / CSV |

**Estadisticas esperadas (jet stream):**
- Media: ~57 kt
- Picos: hasta ~213 kt
- Componente headwind/tailwind significativa para AirTime

**Hashes SHA-256:**

| Archivo | SHA-256 |
|---|---|
| `open_meteo/wind_250hPa_2024.csv` | `103bcc6bdcf92b4976affff7433ac19e928690fd1dbefd5e1a8f798efdcca6cb` |

---

### 3. IEM ASOS/METAR (Ceiling & Visibility)

| Campo | Valor |
|---|---|
| **Proveedor** | Iowa Environmental Mesonet (IEM) |
| **URL** | https://mesonet.agron.iastate.edu/request/download.phtml |
| **Estaciones** | ASOS/METAR en 20 Core Hubs FAA |
| **Variables** | `skyc1` (ceiling), `vsby` (visibility en millas) |
| **Periodo** | Febrero 2024 — Diciembre 2025 |
| **Granularidad temporal** | Observaciones (~cada 20-60 min) |
| **Fecha de extraccion** | `2026-11-27` |
| **Formato** | CSV |
| **Sentinels** | "M" = Missing → NaN |

**Hashes SHA-256:**

| Archivo | SHA-256 |
|---|---|
| `iem/asos_metar_2024.csv` | `8f3e280b440aab31d96564a8347bebc23d6ecd84d109d4fb30e448cb004871ca` |

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

*Ultima actualizacion: 2026-11-27*
