"""
OpenSky Network data ingest (opensky_ingest.py)

Fetches EETN (Tallinn Airport) arrivals and departures for one UTC calendar
day and loads them into the PostgreSQL staging schema.

Usage:
  python opensky_ingest.py               # fetches yesterday
  python opensky_ingest.py --date 2026-05-24  # backfill a specific day
"""

import argparse
import logging
import os
import time
from datetime import date, datetime, timedelta, timezone

import psycopg2
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

AIRPORT = "EETN"
OPENSKY_BASE_URL = "https://opensky-network.org/api/flights"
OPENSKY_TOKEN_URL = (
    "https://auth.opensky-network.org/auth/realms/opensky-network"
    "/protocol/openid-connect/token"
)
TOKEN_EXPIRY_BUFFER = 60


# --- Token Manager ---

class TokenManager:
    """
    Fetches and caches an OAuth2 Bearer token (client credentials flow).
    Automatically re-fetches before the token expires.
    """

    def __init__(self):
        self._client_id = os.environ.get("OPENSKY_CLIENT_ID")
        self._client_secret = os.environ.get("OPENSKY_CLIENT_SECRET")
        self._access_token: str | None = None
        self._expires_at: float = 0.0

        if not self.is_configured():
            logger.warning(
                "OPENSKY_CLIENT_ID / OPENSKY_CLIENT_SECRET not set — "
                "requests will be unauthenticated (strict rate limits apply)"
            )

    def is_configured(self) -> bool:
        return bool(self._client_id and self._client_secret)

    def get_token(self) -> str | None:
        if not self.is_configured():
            return None
        if time.time() >= self._expires_at:
            self._fetch_token()
        return self._access_token

    def _fetch_token(self):
        logger.info("Fetching new OpenSky OAuth2 token.")
        resp = requests.post(
            OPENSKY_TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
            timeout=15,
        )
        resp.raise_for_status()
        payload = resp.json()
        self._access_token = payload["access_token"]
        self._expires_at = time.time() + payload["expires_in"] - TOKEN_EXPIRY_BUFFER
        logger.info("Token acquired, valid for %ds.", payload["expires_in"])


# --- API Client ---

class OpenSkyClient:

    def __init__(self, token_manager: TokenManager):
        self._token_manager = token_manager

    def fetch_arrivals(self, begin: int, end: int) -> list:
        return self._get("arrival", begin, end)

    def fetch_departures(self, begin: int, end: int) -> list:
        return self._get("departure", begin, end)

    def _get(self, endpoint: str, begin: int, end: int) -> list:
        url = f"{OPENSKY_BASE_URL}/{endpoint}"
        token = self._token_manager.get_token()
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        logger.info("GET %s  begin=%s  end=%s", url, begin, end)
        resp = requests.get(
            url,
            headers=headers,
            params={"airport": AIRPORT, "begin": begin, "end": end},
            timeout=30,
        )
        if resp.status_code == 404:
            logger.info("No data for %s (404) — skipping.", url)
            return []
        resp.raise_for_status()
        return resp.json() or []


# --- Database ---

def get_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        port=os.environ.get("DB_PORT", "5432"),
        user=os.environ.get("DB_USER", "lennujaam"),
        password=os.environ.get("DB_PASSWORD", "lennu_grupp"),
        dbname=os.environ.get("DB_NAME", "lennujaam_db"),
    )


SCHEMA_SQL = "CREATE SCHEMA IF NOT EXISTS staging;"

ARRIVALS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS staging.arrivals (
    icao24                              TEXT,
    first_seen                          TIMESTAMP WITH TIME ZONE,
    est_departure_airport               TEXT,
    last_seen                           TIMESTAMP WITH TIME ZONE,
    est_arrival_airport                 TEXT,
    callsign                            TEXT,
    est_departure_airport_horiz_dist    INT,
    est_departure_airport_vert_dist     INT,
    est_arrival_airport_horiz_dist      INT,
    est_arrival_airport_vert_dist       INT,
    departure_airport_candidates_count  INT,
    arrival_airport_candidates_count    INT,
    loaded_at                           TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (icao24, first_seen)
);
"""

DEPARTURES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS staging.departures (
    icao24                              TEXT,
    first_seen                          TIMESTAMP WITH TIME ZONE,
    est_departure_airport               TEXT,
    last_seen                           TIMESTAMP WITH TIME ZONE,
    est_arrival_airport                 TEXT,
    callsign                            TEXT,
    est_departure_airport_horiz_dist    INT,
    est_departure_airport_vert_dist     INT,
    est_arrival_airport_horiz_dist      INT,
    est_arrival_airport_vert_dist       INT,
    departure_airport_candidates_count  INT,
    arrival_airport_candidates_count    INT,
    loaded_at                           TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (icao24, first_seen)
);
"""

ETL_LOG_SQL = """
CREATE TABLE IF NOT EXISTS staging.etl_log (
    id          SERIAL PRIMARY KEY,
    source      TEXT NOT NULL,
    started_at  TIMESTAMP WITH TIME ZONE NOT NULL,
    finished_at TIMESTAMP WITH TIME ZONE,
    rows_loaded INT DEFAULT 0,
    status      TEXT DEFAULT 'running',
    error_msg   TEXT
);
"""

UPSERT_SQL = """
INSERT INTO staging.{table} (
    icao24, first_seen, est_departure_airport, last_seen, est_arrival_airport,
    callsign, est_departure_airport_horiz_dist, est_departure_airport_vert_dist,
    est_arrival_airport_horiz_dist, est_arrival_airport_vert_dist,
    departure_airport_candidates_count, arrival_airport_candidates_count, loaded_at
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
ON CONFLICT (icao24, first_seen) DO UPDATE SET
    est_departure_airport              = EXCLUDED.est_departure_airport,
    last_seen                          = EXCLUDED.last_seen,
    est_arrival_airport                = EXCLUDED.est_arrival_airport,
    callsign                           = EXCLUDED.callsign,
    est_departure_airport_horiz_dist   = EXCLUDED.est_departure_airport_horiz_dist,
    est_departure_airport_vert_dist    = EXCLUDED.est_departure_airport_vert_dist,
    est_arrival_airport_horiz_dist     = EXCLUDED.est_arrival_airport_horiz_dist,
    est_arrival_airport_vert_dist      = EXCLUDED.est_arrival_airport_vert_dist,
    departure_airport_candidates_count = EXCLUDED.departure_airport_candidates_count,
    arrival_airport_candidates_count   = EXCLUDED.arrival_airport_candidates_count,
    loaded_at                          = NOW();
"""


def ensure_tables(conn):
    with conn.cursor() as cur:
        cur.execute(SCHEMA_SQL)
        cur.execute(ARRIVALS_TABLE_SQL)
        cur.execute(DEPARTURES_TABLE_SQL)
        cur.execute(ETL_LOG_SQL)
    conn.commit()


def log_start(conn, source: str) -> int:
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO staging.etl_log (source, started_at) VALUES (%s, NOW()) RETURNING id;",
            (source,),
        )
        log_id = cur.fetchone()[0]
    conn.commit()
    return log_id


def log_finish(conn, log_id: int, rows: int, status="success", error_msg=None):
    with conn.cursor() as cur:
        cur.execute(
            """UPDATE staging.etl_log
               SET finished_at = NOW(), rows_loaded = %s, status = %s, error_msg = %s
               WHERE id = %s;""",
            (rows, status, error_msg, log_id),
        )
    conn.commit()


# --- Ingest ---

def ingest_endpoint(conn, client: OpenSkyClient, endpoint: str, begin: int, end: int):
    """Fetch one endpoint (arrival/departure) and upsert into staging."""
    table = "arrivals" if endpoint == "arrival" else "departures"
    source = f"opensky/{endpoint}/{AIRPORT}"
    log_id = log_start(conn, source)
    rows = 0

    try:
        fetcher = client.fetch_arrivals if endpoint == "arrival" else client.fetch_departures
        flights = fetcher(begin, end)

        skipped = 0
        with conn.cursor() as cur:
            for f in flights:
                if not f.get("icao24") or not f.get("firstSeen"):
                    skipped += 1
                    continue
                cur.execute(
                    UPSERT_SQL.format(table=table),
                    (
                        f["icao24"],
                        datetime.fromtimestamp(f["firstSeen"], tz=timezone.utc),
                        f.get("estDepartureAirport"),
                        datetime.fromtimestamp(f["lastSeen"], tz=timezone.utc) if f.get("lastSeen") else None,
                        f.get("estArrivalAirport"),
                        (f.get("callsign") or "").strip() or None,
                        f.get("estDepartureAirportHorizDistance"),
                        f.get("estDepartureAirportVertDistance"),
                        f.get("estArrivalAirportHorizDistance"),
                        f.get("estArrivalAirportVertDistance"),
                        f.get("departureAirportCandidatesCount"),
                        f.get("arrivalAirportCandidatesCount"),
                    ),
                )
                rows += 1

        if skipped:
            logger.warning("Skipped %d flight(s) with missing icao24 or firstSeen.", skipped)

        conn.commit()
        logger.info("Loaded %d rows into staging.%s.", rows, table)
        log_finish(conn, log_id, rows)

    except Exception as e:
        conn.rollback()
        logger.error("Failed (%s): %s", source, e)
        log_finish(conn, log_id, rows, status="error", error_msg=str(e))
        raise


def run(target_date: date | None = None, days: int = 1):
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).date()
    end_day = target_date or yesterday
    start_day = end_day - timedelta(days=days - 1)

    token_manager = TokenManager()
    client = OpenSkyClient(token_manager)

    conn = get_connection()
    try:
        ensure_tables(conn)
        day = start_day
        while day <= end_day:
            day_start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
            day_end = day_start + timedelta(days=1)
            begin = int(day_start.timestamp())
            end = int(day_end.timestamp())

            logger.info("--- %s ---", day)
            ingest_endpoint(conn, client, "arrival", begin, end)
            ingest_endpoint(conn, client, "departure", begin, end)
            day += timedelta(days=1)
    finally:
        conn.close()

    logger.info("Done — %d day(s) ingested.", days)


# --- Entry point ---

def main():
    parser = argparse.ArgumentParser(description="OpenSky ingest for EETN.")
    parser.add_argument(
        "--date",
        type=date.fromisoformat,
        default=None,
        help="Last UTC date to fetch (YYYY-MM-DD). Defaults to yesterday.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=1,
        help="Number of days to fetch ending on --date (default 1).",
    )
    args = parser.parse_args()
    run(args.date, args.days)


if __name__ == "__main__":
    main()
