"""
Airport seed ingestion script.

Downloads airport reference data from OurAirports and writes it
to the dbt seeds directory.

Usage:
    python ingest.py
"""

import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

AIRPORTS_CSV_URL = "https://ourairports.com/data/airports.csv"

SEEDS_DIR = Path("/dbt/seeds")


def load_airports_seed():
    SEEDS_DIR.mkdir(parents=True, exist_ok=True)

    output_file = SEEDS_DIR / "airports.csv"

    logger.info("Downloading airport data from %s", AIRPORTS_CSV_URL)

    df = pd.read_csv(AIRPORTS_CSV_URL)

    logger.info("Downloaded %d airports", len(df))

    # Keep only airports with scheduled service
    df = df[df["scheduled_service"] == "yes"]

    # Rename columns used in dbt
    df = df.rename(
        columns={
            "iata_code": "iata",
            "icao_code": "icao",
        }
    )

    # Keep only airports that have an ICAO code
    # because OpenSky uses ICAO airport identifiers
    df = df[df["icao"].notna()]

    # Ensure ICAO codes are unique
    df = df.drop_duplicates(subset=["icao"])

    df = df[
        [
            "id",
            "ident",
            "type",
            "name",
            "municipality",
            "iso_country",
            "iata",
            "icao",
            "latitude_deg",
            "longitude_deg",
        ]
    ]

    df.to_csv(output_file, index=False)

    logger.info(
        "Airport seed written to %s (%d rows)",
        output_file,
        len(df),
    )


if __name__ == "__main__":
    load_airports_seed()

#
#
#
#
# """
# Andmete sissetoomise skript (ingest.py)
#
# Laadib lennujaamade andmed ourairports.com-ist ja kirjutab need dbt seeds kausta.
#
# Kasutamine:
#   python ingest.py
# """
#
# import logging
# from pathlib import Path
#
# import pandas as pd
#
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s [%(levelname)s] %(message)s",
# )
# logger = logging.getLogger(__name__)
#
# AIRPORTS_CSV_URL = "https://ourairports.com/data/airports.csv"
#
# # BASE_DIR = Path(__file__).resolve().parent.parent
# # SEEDS_DIR = BASE_DIR / "dbt_project" / "seeds"
#
# SEEDS_DIR = Path("/dbt/seeds")
#
#
# def load_airports_seed():
#     SEEDS_DIR.mkdir(parents=True, exist_ok=True)
#     output_file = SEEDS_DIR / "airports.csv"
#
#     logger.info("Laadin lennujaamade andmeid: %s", AIRPORTS_CSV_URL)
#     df = pd.read_csv(AIRPORTS_CSV_URL)
#
#     df = df[df["scheduled_service"] == "yes"]
#
#     df = df.rename(columns={"iata_code": "iata", "icao_code": "icao"})
#
#     df = df[
#         [
#             "id",
#             "ident",
#             "type",
#             "name",
#             "municipality",
#             "iso_country",
#             "iata",
#             "icao",
#             "latitude_deg",
#             "longitude_deg",
#         ]
#     ]
#
#     df.to_csv(output_file, index=False)
#     logger.info("Seemefail kirjutatud: %s (%d rida)", output_file, len(df))
#
#
# if __name__ == "__main__":
#     load_airports_seed()
