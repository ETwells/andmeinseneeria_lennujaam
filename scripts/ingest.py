"""
Andmete sissetoomise skript (ingest.py)

Laadib lennujaamade andmed ourairports.com-ist ja kirjutab need dbt seeds kausta.

Kasutamine:
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

    logger.info("Laadin lennujaamade andmeid: %s", AIRPORTS_CSV_URL)
    df = pd.read_csv(AIRPORTS_CSV_URL)

    df = df[df["scheduled_service"] == "yes"]

    df = df.rename(columns={"iata_code": "iata", "icao_code": "icao"})

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
    logger.info("Seemefail kirjutatud: %s (%d rida)", output_file, len(df))


if __name__ == "__main__":
    load_airports_seed()
