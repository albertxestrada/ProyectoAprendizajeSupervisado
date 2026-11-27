"""
Script para reproducir la descarga de datos crudos.

Uso:
    python data/raw/download_data.py --source bts
    python data/raw/download_data.py --source open_meteo
    python data/raw/download_data.py --source iem
    python data/raw/download_data.py --source all

Nota: BTS requiere descarga manual desde la web. Este script
documenta los pasos y descarga automaticamente Open-Meteo e IEM.
"""

import argparse
import sys
from pathlib import Path
from datetime import date, timedelta

# Agregar raiz del proyecto al path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from config import CORE_HUBS, PRESSURE_LEVEL_HPA, DATA_START, DATA_END


# ============================================================================
# Coordenadas de los 20 Core Hubs (lat, lon)
# ============================================================================
HUB_COORDS = {
    "ATL": (33.6407, -84.4277),
    "DFW": (32.8998, -97.0403),
    "DEN": (39.8561, -104.6737),
    "ORD": (41.9742, -87.9073),
    "LAX": (33.9425, -118.4081),
    "CLT": (35.2140, -80.9431),
    "MCO": (28.4312, -81.3081),
    "LAS": (36.0840, -115.1537),
    "PHX": (33.4373, -112.0078),
    "MIA": (25.7959, -80.2870),
    "SEA": (47.4502, -122.3088),
    "IAH": (29.9902, -95.3368),
    "JFK": (40.6413, -73.7781),
    "EWR": (40.6895, -74.1745),
    "SFO": (37.6213, -122.3790),
    "MSP": (44.8848, -93.2223),
    "BOS": (42.3656, -71.0096),
    "DTW": (42.2124, -83.3534),
    "FLL": (26.0742, -80.1506),
    "PHL": (39.8744, -75.2424),
}

# Mapping IATA -> ICAO para IEM
IATA_TO_ICAO = {
    "ATL": "KATL", "DFW": "KDFW", "DEN": "KDEN", "ORD": "KORD",
    "LAX": "KLAX", "CLT": "KCLT", "MCO": "KMCO", "LAS": "KLAS",
    "PHX": "KPHX", "MIA": "KMIA", "SEA": "KSEA", "IAH": "KIAH",
    "JFK": "KJFK", "EWR": "KEWR", "SFO": "KSFO", "MSP": "KMSP",
    "BOS": "KBOS", "DTW": "KDTW", "FLL": "KFLL", "PHL": "KPHL",
}


def download_bts():
    """
    Descarga los zips mensuales de BTS On-Time Performance entre
    DATA_START y DATA_END (config.py) y guarda un CSV por mes.

    Salida: data/raw/bts/on_time_2024_02.csv ... on_time_2025_12.csv
    """
    import requests
    import zipfile
    import pandas as pd
    from io import BytesIO
    from src.utils import file_sha256

    print("=" * 60)
    print("  BTS On-Time Performance")
    print("=" * 60)

    output_dir = PROJECT_ROOT / "data" / "raw" / "bts"
    output_dir.mkdir(parents=True, exist_ok=True)

    base_url = (
        "https://transtats.bts.gov/PREZIP/"
        "On_Time_Reporting_Carrier_On_Time_Performance_1987_present_{y}_{m}.zip"
    )

    months = pd.period_range(DATA_START, DATA_END, freq="M")
    failed = []

    for p in months:
        target = output_dir / f"on_time_{p.year}_{p.month:02d}.csv"

        if target.exists():
            print(f"  {target.name} ya existe, se omite")
            continue

        url = base_url.format(y=p.year, m=p.month)
        print(f"  Descargando {p.year}-{p.month:02d}...")

        try:
            resp = requests.get(url, timeout=600)
            resp.raise_for_status()

            with zipfile.ZipFile(BytesIO(resp.content)) as zf:
                csv_names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
                if not csv_names:
                    raise ValueError("El zip no contiene ningun CSV")
                with zf.open(csv_names[0]) as src, open(target, "wb") as dst:
                    dst.write(src.read())

            print(f"    OK: {target.name} (SHA-256: {file_sha256(str(target))})")

        except Exception as e:
            print(f"    ERROR {p}: {e}")
            failed.append(str(p))

    print()
    if failed:
        print(f"Meses con error: {failed}")
        print("Reintenta con: python data/raw/download_data.py --source bts")
    else:
        print(f"Descarga completa ({len(months)} meses) en: {output_dir}")
    print("-> Registrar los hashes SHA-256 en data/data_contract.md")


def download_open_meteo():
    """
    Descarga datos de viento a 250 hPa desde Open-Meteo Previous Runs API.
    """
    try:
        import openmeteo_requests
        import pandas as pd
    except ImportError:
        print("ERROR: Instalar dependencias: pip install openmeteo-requests pandas")
        return

    print("=" * 60)
    print("  Open-Meteo — Viento 250 hPa (Jet Stream)")
    print("=" * 60)

    output_dir = PROJECT_ROOT / "data" / "raw" / "open_meteo"
    output_dir.mkdir(parents=True, exist_ok=True)

    om = openmeteo_requests.Client()
    all_data = []

    for iata, (lat, lon) in HUB_COORDS.items():
        print(f"  Descargando {iata} ({lat}, {lon})...")

        try:
            params = {
                "latitude": lat,
                "longitude": lon,
                "start_date": DATA_START,
                "end_date": DATA_END,
                "hourly": [
                    f"wind_speed_{PRESSURE_LEVEL_HPA}hPa",
                    f"wind_direction_{PRESSURE_LEVEL_HPA}hPa",
                ],
                "timezone": "UTC",
            }

            responses = om.weather_api(
                "https://previous-runs-api.open-meteo.com/v1/forecast",
                params=params,
            )

            response = responses[0]
            hourly = response.Hourly()

            timestamps = pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left",
            )

            df = pd.DataFrame({
                "timestamp_utc": timestamps,
                "airport": iata,
                f"wind_speed_{PRESSURE_LEVEL_HPA}hPa": hourly.Variables(0).ValuesAsNumpy(),
                f"wind_direction_{PRESSURE_LEVEL_HPA}hPa": hourly.Variables(1).ValuesAsNumpy(),
            })

            all_data.append(df)
            print(f"    OK: {len(df)} registros")

        except Exception as e:
            print(f"    ERROR en {iata}: {e}")

    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        output_path = output_dir / f"wind_{PRESSURE_LEVEL_HPA}hPa_2024.csv"
        combined.to_csv(output_path, index=False)
        print(f"\nGuardado: {output_path}")
        print(f"Total: {len(combined):,} registros")

        # Registrar hash
        from src.utils import file_sha256
        sha = file_sha256(str(output_path))
        print(f"SHA-256: {sha}")
        print("-> Registrar en data/data_contract.md")


def download_iem():
    """
    Descarga datos ASOS/METAR desde Iowa Environmental Mesonet.
    """
    try:
        import requests
        import pandas as pd
    except ImportError:
        print("ERROR: Instalar dependencias: pip install requests pandas")
        return

    print("=" * 60)
    print("  IEM ASOS/METAR — Ceiling & Visibility")
    print("=" * 60)

    output_dir = PROJECT_ROOT / "data" / "raw" / "iem"
    output_dir.mkdir(parents=True, exist_ok=True)

    # IEM CGI endpoint
    base_url = "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py"

    all_data = []
    icao_stations = list(IATA_TO_ICAO.values())
    end_exclusive = date.fromisoformat(DATA_END) + timedelta(days=1)

    for iata, icao in IATA_TO_ICAO.items():
        print(f"  Descargando {iata} ({icao})...")

        params = {
            "station": icao,
            "data": ["skyc1", "vsby"],
            "year1": int(DATA_START[:4]), "month1": int(DATA_START[5:7]),
            "day1": int(DATA_START[8:10]),
            "year2": end_exclusive.year, "month2": end_exclusive.month,
            "day2": end_exclusive.day,
            "tz": "UTC",
            "format": "comma",
            "latlon": "no",
            "elev": "no",
            "missing": "M",
            "trace": "T",
            "report_type": [1, 2],  # METAR + SPECI
        }

        try:
            resp = requests.get(base_url, params=params, timeout=60)
            resp.raise_for_status()

            # IEM devuelve CSV con cabecera comentada (#)
            lines = resp.text.strip().split("\n")
            data_lines = [l for l in lines if not l.startswith("#")]

            if len(data_lines) > 1:
                from io import StringIO
                df = pd.read_csv(StringIO("\n".join(data_lines)))
                df["airport_iata"] = iata
                all_data.append(df)
                print(f"    OK: {len(df)} observaciones")
            else:
                print(f"    WARN: Sin datos para {icao}")

        except Exception as e:
            print(f"    ERROR en {icao}: {e}")

    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        output_path = output_dir / "asos_metar_2024.csv"
        combined.to_csv(output_path, index=False)
        print(f"\nGuardado: {output_path}")
        print(f"Total: {len(combined):,} observaciones")

        from src.utils import file_sha256
        sha = file_sha256(str(output_path))
        print(f"SHA-256: {sha}")
        print("-> Registrar en data/data_contract.md")


def main():
    parser = argparse.ArgumentParser(description="Descarga datos crudos para el proyecto")
    parser.add_argument(
        "--source",
        choices=["bts", "open_meteo", "iem", "all"],
        required=True,
        help="Fuente de datos a descargar",
    )
    args = parser.parse_args()

    if args.source == "bts" or args.source == "all":
        download_bts()
        print()

    if args.source == "open_meteo" or args.source == "all":
        download_open_meteo()
        print()

    if args.source == "iem" or args.source == "all":
        download_iem()
        print()


if __name__ == "__main__":
    main()
