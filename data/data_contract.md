# Data Contract — Anticipando el caos aéreo

Este documento define qué datos usa el proyecto, cuándo están disponibles, cómo se
identifican y cómo se reproducen. La fuente autoritativa de integridad es
`data/manifest.csv`; sus rutas son relativas al directorio `data/`.

## 1. Identidad

| Campo | Valor |
|---|---|
| **Proyecto** | Anticipando el caos aéreo mediante Machine Learning |
| **Unidad de observación** | Un vuelo nacional sin escala, programado en EE. UU. |
| **Clave propuesta** | `Reporting_Airline`, `Flight_Number_Reporting_Airline`, `FlightDate`, `OriginAirportID` |
| **Momento de corte** | T−4 h respecto a `CRSDepTime` en UTC |
| **Periodo disponible** | 2024-02-01 a 2025-12-31 |
| **Responsable de datos** | Juan Camilo Bolaños Aldana |
| **Objetivo inmediato** | Preprocesamiento auditable y protección frente a fuga temporal |
| **Archivo de integridad** | `data/manifest.csv` |

El periodo real disponible comienza en febrero de 2024. La documentación anterior
que incluía enero de 2024 no corresponde a una extracción presente en el repositorio.

## 2. Propósito

El pasajero decide antes de acudir al aeropuerto si modifica su recogida, conexión
o agenda. El corte es T−4 h: el modelo no puede usar información conocida
posteriormente, incluidos tiempos reales, cancelación efectiva, matrícula real,
tiempos en pista, causas en minutos o datos meteorológicos observados después del corte.

Las variables de destino se construyen separadamente y no pueden regresar a `X`:
`ArrDelay`, `ArrDelayMinutes`, `ArrDel15`, causas de demora, cancelación y columnas
operativas reales.

## 3. Esquema

### BTS On-Time Performance

| Campo | Valor |
|---|---|
| **Proveedor** | Bureau of Transportation Statistics (BTS) |
| **URL** | https://transtats.bts.gov/PREZIP/ |
| **Archivos** | `raw/bts/on_time_2024_02.csv` a `raw/bts/on_time_2025_12.csv` |
| **Frecuencia** | Una extracción CSV por mes |
| **Formato** | CSV separado por comas |
| **Zona horaria** | Horas locales originales; normalizar a UTC en preprocesamiento |
| **Fecha/hora de extracción** | Incluidas por cada archivo en `data/manifest.csv` |
| **Uso previsto** | Vuelo, ruta, horario programado, aerolínea y etiquetas de resultado |

Campos esperados de entrada antes de quitar fuga:
`FlightDate`, `Reporting_Airline`, `Flight_Number_Reporting_Airline`,
`Origin`, `OriginAirportID`, `Dest`, `CRSDepTime`, `CRSArrTime`,
`CRSElapsedTime`, `Distance`, `DepDelay`, `ArrDelay`, `ArrDelayMinutes`,
`ArrDel15`, `AirTime`, `Cancelled`, `CancellationCode`, `Diverted`,
`CarrierDelay`, `WeatherDelay`, `NASDelay`, `SecurityDelay`,
`LateAircraftDelay`, `Tail_Number`.

Los tiempos reales, cancelación efectiva, matrícula real, causas y métricas
posteriores al vuelo son etiquetas o variables prohibidas. Se usan únicamente
después de construir las etiquetas y antes de eliminar las columnas del dataset
de modelado.

### Open-Meteo Previous Runs

| Campo | Valor |
|---|---|
| **Proveedor** | Open-Meteo |
| **API** | Previous Runs API |
| **Endpoint** | `https://previous-runs-api.open-meteo.com/v1/forecast` |
| **Variables disponibles** | Viento a 250 hPa y viento a 10 m por día previo |
| **Granularidad** | Horaria |
| **Coordenadas** | Aeropuertos IATA o estaciones configuradas |
| **Zona horaria** | UTC |
| **Formato** | CSV |
| **Fecha/hora de extracción** | Incluidas en `data/manifest.csv` |

La fuente se denomina **pronóstico archivado**. `Previous Runs` conserva ejecuciones
pasadas del pronóstico: no debe describirse como reanálisis ni como observación
meteorológica posterior al vuelo. Las series disponibles son:

- `raw/open_meteo/wind_250hPa_2024.csv`: archivo legado a 250 hPa, excluido de
  modelado hasta completar su trazabilidad temporal.
- `raw/open_meteo/wind_10m_previous_day1_2024_2025.csv`: pronósticos previos
  con desfase de un día.

### IEM ASOS/METAR

| Campo | Valor |
|---|---|
| **Proveedor** | Iowa Environmental Mesonet (IEM) |
| **Endpoint** | `https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py` |
| **Estaciones** | 20 aeropuertos Core Hub FAA |
| **Variables** | `skyc1` (techo), `vsby` (visibilidad) |
| **Granularidad** | Observaciones METAR/SPECI, aproximadamente cada 20-60 minutos |
| **Zona horaria** | UTC |
| **Formato** | CSV |
| **Centinelas** | `M` indica ausente y debe convertirse a valor nulo |
| **Archivo** | `raw/iem/asos_metar_2024.csv` |
| **Fecha/hora de extracción** | Incluida en `data/manifest.csv` |

## 4. Calidad

- Los hashes SHA-256 se calculan con `src/utils.file_sha256()`.
- Los tamaños y hashes de los 26 archivos inventariados coinciden con el manifiesto.
- Se debe comprobar la existencia de archivos antes de concatenar BTS, IEM u Open-Meteo.
- Los vuelos cancelados se mantienen temporalmente para calcular retrasos recientes
  y se excluyen después de la construcción de las etiquetas.
- Los CSV meteorológicos pueden contener distintos esquemas de columnas; las cargas
  deben normalizar nombres y tipos de forma explícita.
- El valor `M` de IEM se trata como dato ausente, no como cadena.
- Toda hora fuente debe conservarse junto con su hora UTC normalizada.
- Las muestras sin zona horaria válida quedan sujetas a cuarentena hasta P4.

## 5. Servicio

- El repositorio entrega los datos crudos en `data/raw/` para reproducir el
  preprocesamiento local.
- `data/raw/download_data.py` permite reproducir las descargas automáticas de
  Open-Meteo e IEM; BTS requiere descargar o regenerar los CSV mensuales mediante
  `PREZIP`.
- Cada ejecución que use datos crudos debe registrar:
  - versión o commit del código;
  - rutas de entrada;
  - parámetros de partición;
  - tamaño y SHA-256;
  - fecha UTC de ejecución;
  - outputs generados.
- Las variables modelables deben validarse frente a una futura lista blanca
  `FEATURES_ALLOWED` en `config.py`.
- `FEATURES_ALLOWED` sustituye la exclusión por listas negras de fuga. Un DataFrame
  de características pasa la comprobación `validate_features()` antes de modelar.

## 6. Evolución

- Una nueva fuente o archivo debe actualizar `data/manifest.csv` y este contrato.
- Si cambia el periodo, la población o el momento de corte, se debe versionar el
  contrato y conservar el manifiesto anterior.
- Los cambios de esquema requieren un diagnóstico de compatibilidad y una prueba
  en P2-P4.
- Los datos crudos no se sobrescriben: una extracción nueva recibe otra copia,
  una fila nueva en el manifiesto y una fecha UTC registrada.
- Los periodos meteorológicos e históricos deben ampliar o cambiar solo cuando su
  disponibilidad respete T−4 h.

## Política de acceso y términos de uso

Los datos proceden de proveedores públicos. Antes de redistribuirlos fuera del
entorno académico, se deben revisar las condiciones vigentes de BTS, Open-Meteo
e IEM. Este contrato registra sus endpoints, pero no constituye una licencia
explícita del proveedor.

## 20 Core Hubs actuales

| IATA | Zona IANA |
|---|---|
| ATL | America/New_York |
| DFW | America/Chicago |
| DEN | America/Denver |
| ORD | America/Chicago |
| LAX | America/Los_Angeles |
| CLT | America/New_York |
| MCO | America/New_York |
| LAS | America/Los_Angeles |
| PHX | America/Phoenix |
| MIA | America/New_York |
| SEA | America/Los_Angeles |
| IAH | America/Chicago |
| JFK | America/New_York |
| EWR | America/New_York |
| SFO | America/Los_Angeles |
| MSP | America/Chicago |
| BOS | America/New_York |
| DTW | America/New_York |
| FLL | America/New_York |
| PHL | America/New_York |

## Cierre P1

- Estado: completado.
- Evidencia: todas las rutas y hashes del manifiesto se verificaron contra
  `data/raw/` el 2026-11-27.
- Pendiente deliberado para P2-P6: lista blanca, correcciones de carga,
  UTC por aeropuerto, etiquetas y ventana temporal.
