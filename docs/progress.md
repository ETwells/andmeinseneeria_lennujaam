# Edenemisraport

Tallinna lennujaama (EETN) marsruutide ja nädalamustrite uuring. Andmevoog: OpenSky API → `staging` → dbt (`silver` / `marts`) → Superset.

> **Branchide seis:** `main` sisaldab sissevõttu + `staging` kihti; transformatsioonid, testid ja dashboard on `superset` branchis (ehitatud `dbt_meik` peale), veel `main`-i merge'imata.

## Mis on valmis

- Docker Compose käivitab kõik teenused (pgduckdb, dbt, Superset, ingest).
- OpenSky API-st laetakse EETN saabumised/väljumised `staging` kihti; iga käivitus logitakse `etl_log`-i, ingest kordub kord ööpäevas.
- Viiteandmed valmis (`airports` seeme OurAirportsist).
- dbt `silver` *(superset)*: `silver_dim_arrivals` / `silver_dim_departures` ühendavad lennud lennujaamadega + Tallinna kohaaeg.
- dbt `marts` *(superset)*: dimensioonid `dim_date` (Eesti pühad) ja `dim_time`.
- Andmekvaliteedi testid läbivad *(superset)*: `not_null`, `unique`, `unique_combination_of_columns` + seed tests.
- Superset dashboard *(superset)*: 2 chart'i (lennud kellaaja ja nädalapäeva lõikes), eksport ZIP commit'itud.

## Järgmised sammud

- Merge'ida `dbt_meik` + `superset` → `main`.
- Lisada 2 puuduvat mõõdikut: top 10 marsruuti ja unikaalsed sihtkohad.
- Lisada testid: `relationships`, `accepted_values`, source freshness.
- Viimistleda README.

## Mis takistab

- Integratsioon: valmis töö on branchides, `main`-i merge'imata — konfliktirisk kasvab (`dbt_project/` → `dbt/` ümbernimetus).
- OpenSky autentimata päringutel ranged limiidid (`OPENSKY_CLIENT_ID` / `OPENSKY_CLIENT_SECRET` `.env`-i).
- Ingest tõmbab korraga ühe päeva (vaikimisi eilse) ja jookseb kord ööpäevas. Seega ühe päeva andmetest ei näe veel mustrit - ideaalis võiks olla vähemalt nädala andmed, et näha sisukamat nädalamustri charti.

## Kontrollpunkt

```bash
git checkout superset
docker compose up -d
docker compose exec ingest python opensky_ingest.py
docker compose exec dbt dbt seed
docker compose exec dbt dbt build
```

Oodatav tulemus: `dbt build` ehitab mudelid (`silver_dim_arrivals` / `departures`, `dim_date`, `dim_time`) ja testid läbivad (`PASS`). Dashboardi nägemiseks impordi `superset/exports/dashboard_export_*.zip` Superseti UI-s (localhost:8088).
