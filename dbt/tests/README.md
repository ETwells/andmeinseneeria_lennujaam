# Testikomplekt (dbt) — Tallinna lennujaama projekt

See kaust sisaldab **kohandatud (singular) SQL-teste**, mis kontrollivad
projekti äriloogikat. Üldised (generic) testid — `not_null`, `unique`,
`accepted_values`, `relationships`, `dbt_utils.*` — on kirjeldatud mudelite
juures `schema.yml` / `models.yml` failides.

## Kuidas test töötab

Iga kohandatud test on SQL-päring, mis **valib reeglit rikkuvad read**.

- Päring tagastab **0 rida** ⇒ test **läbib** (PASS).
- Päring tagastab **≥ 1 rea** ⇒ test **kukub läbi** (FAIL); tagastatud read
  näitavad täpselt, millised kirjed reeglit rikuvad.

Kuna `dbt_project.yml` failis on `data_tests: +store_failures: true`,
salvestatakse iga ebaõnnestunud testi read eraldi tabelisse
(skeem `*_dbt_test__audit`), kus neid saab järelkontrolliks vaadata.

## Testide sisu

### Kohandatud testid (`dbt/tests/*.sql`)

| Fail | Mudel | Mida kontrollib |
|---|---|---|
| `assert_obt_tll_involvement.sql` | `OBT_TLL_arrivals_departures` | Iga faktirida on seotud Tallinnaga: `arrival_TLL` ⇒ `arrival_iata='TLL'`, `departure_TLL` ⇒ `departure_iata='TLL'`. |
| `assert_obt_event_date_in_dim_date.sql` | `OBT_…` ↔ `dim_date` | Iga `event_date` leidub `dim_date`'is (liitmine ei jää poolikuks). |
| `assert_obt_no_self_loop.sql` | `OBT_…` | Lähte- ja sihtlennujaam ei ole samad (kui mõlemad teada). |
| `assert_dim_date_holiday_not_working_day.sql` | `dim_date` | Nädalavahetus/püha ei ole kunagi tööpäev. |
| `assert_dim_time_exactly_one_daypart.sql` | `dim_time` | Igal real on täpselt üks päevaosa lipp tõene (katavus + välistavus). |
| `assert_silver_arrivals_seen_order.sql` | `silver_dim_arrivals` | `last_seen_utc ≥ first_seen_utc`. |
| `assert_silver_departures_seen_order.sql` | `silver_dim_departures` | `last_seen_utc ≥ first_seen_utc`. |

### Üldised testid (`schema.yml`)

- **sources.yml** — `not_null` (`icao24`, `first_seen`) + värskuskontroll (`loaded_at`).
- **seeds/schema.yml** — `airports`: `not_null` + `unique` (`id`, `icao`).
- **silver/models.yml** — `unique_combination_of_columns` + `not_null`.
- **marts/schema.yml** — `OBT.direction`: `accepted_values`; `dim_date` ja
  `dim_time`: `not_null`, `unique` ja `dbt_utils.accepted_range`
  (tund 0–23, minut 0–59, kuu 1–12, kvartal 1–4, nädalapäev 1–7).

## Kuidas teste käivitada

> Eeldus: Docker on käivitatud ja andmed on API-st sisse loetud
> (vt projekti juurkausta `README.md`). `dbt test` kontrollib juba **ehitatud**
> mudeleid, seega tuleb enne `dbt seed` + `dbt run` (või `dbt build`) käivitada.

```bash
# 1. Käivita teenused
docker compose up -d

# 2. Installi dbt sõltuvused (dbt_utils)
docker compose exec dbt dbt deps

# 3. Laadi seemned (airports) ja ehita mudelid
docker compose exec dbt dbt seed
docker compose exec dbt dbt run

# 4. Käivita KÕIK testid (üldised + kohandatud)
docker compose exec dbt dbt test
```

### Kasulikud valikud

```bash
# Ainult kohandatud (singular) testid sellest kaustast
docker compose exec dbt dbt test --select test_type:singular

# Ainult üldised testid
docker compose exec dbt dbt test --select test_type:generic

# Ühe mudeli testid
docker compose exec dbt dbt test --select OBT_TLL_arrivals_departures

# Üks konkreetne test nime järgi
docker compose exec dbt dbt test --select assert_obt_tll_involvement

# Ehita ja testi korraga (run + test ühe käsuga)
docker compose exec dbt dbt build
```

Ebaõnnestunud testi ridade vaatamine andmebaasis (näide):

```bash
docker exec -it lennujaam_db psql -U lennujaam -d lennujaam_db \
  -c "\dt *dbt_test__audit*"
```
