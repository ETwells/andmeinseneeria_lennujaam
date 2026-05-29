# TALLINNA LENNUJAAMA MARSRUUTIDE UURING


## NB! Kõikide erinevate teenuste autentimisandmed asuvad .env-failis.


## 1. Projekti Struktuur
```
── compose.yml
├── data
├── dbt_project
│   ├── dbt_packages
│   │   └── dbt_utils
│   ├── dbt_project.yml
│   ├── models
│   │   ├── marts
│   │   ├── silver
│   │   └── sources.yml
│   ├── packages.yml
│   ├── profiles.yml
│   ├── seeds
│   └── target
├── Dockerfile.dbt
├── Dockerfile.python
├── Dockerfile.superset
├── docs
│   ├── arhitektuur.md
│   └── progress.md
├── README.md
├── scripts
│   ├── ingest.py
│   └── requirements.txt
└── superset_config.py
```


## Äriküsimus

Millised on Tallinna lennujaama populaarseimad marsruudid nädala lõikes ja kuidas muutub lennuliiklus nädalapäevade lõikes?

> Täpsustus: "populaarseim marsruut" tähendab antud projektis suurimat lennusündmuste arvu, mitte reisijate arvu.

## Mõõdikud

1. **Top 10 sihtkohta ja lähtekohta nädalas** — kõige rohkem lende Tallinna lennujaama ja teise lennujaama vahel.
2. **Nädalamuster** — mis päevadel on kõige rohkem lende.
3. **Tipp-tunnid nädalas** — millistel kellaaegadel on Tallinna lennujaamas kõige rohkem saabumisi ja väljumisi.
4. **Unikaalsed sihtkohad nädalas** — mitme erineva lennujaamaga oli ühendus.

## Andmestik: andmeallikad

| Allikas | Tüüp | Muutuvus ajas | Kasutus |
|---|---|---|---|
| [OpenSky API](https://openskynetwork.github.io/opensky-api/rest.html) | Avalik HTTP API | Uueneb kord päevas öise batch-processiga | Põhiandmevoog: Tallinna lennujaama saabumised ja väljumised |
| [OurAirports CSV](https://ourairports.com/help/data-dictionary.html) | CSV/ dbt seed | Ei, staatiline | Lennujaama nimi ja kood ning linna nimi ja riik |

Põhiandmevoog tuleb OpenSky API-st (endpointid: `GET /flights/arrival` ja `GET /flights/departure`). Päringutes kasutatakse Tallinna lennujaama ICAO koodi `EETN`.

Staatilisest lennujaama nimetuste CSV-st võetakse lennujaama nimi ja kood ning linna nimi ja riik.


## Arhitektuur

![Dataflow architecture and tooling](/images/Lennujaam_ver2.jpg)


<!--<img width="816" height="754" alt="image" src="https://github.com/user-attachments/assets/bc308b37-274f-4fbd-9b5e-9c362a071b1b" />-->

## Stack

| Komponent | Tööriist |
|-----------|---------|
| Sissevõtt | [Python / Airflow ] |
| Transformatsioon | [SQL / dbt ] |
| Andmehoidla | PostgreSQL |
| Näidikulaud | [Superset] |
| Orkestreerimine | [Airflow / cron] |


## Andmevoog ja Andmebaasi kihid

| Kiht | Roll |
|---|---|
| `seeds` | Hoiab staatilist andmekogumid, mida salvestatakse projekti sees .csv-failina ja laaditakse andmelattu tabelina. |
| `staging` | Hoiab API-st saadud lendude infot võimalikult allikalähedaselt |
| `intermediate` | Puhastatud ja rikastatud lennuandmed |
| `marts` | Agregeeritud andmed Superset'i jaoks |

Iga töövoo käivitus saab uue `run_id`. Vanad API vastused jäävad `staging` kihti alles. Antud projektis `seeds` on ette nähtud viiteandmete jaoks, milleks on lennujaama nimi ja kood ning linna nimi ja riik.
`intermediate` kihis tehakse eelmodifikatsioone, st filtreerimine, andmetüüpide korrastamine, tabelite basic joins, jne.

`marts` tabelid esitavad `star_Schema`' andmemudelit ning on ettenähtud püstitatud äriküsimusele vastamiseks läbi defineeritud KPI-de. Samuti `marts` tabelid sisaldavad kõigi käivituste andmeid (Superset filtreerib viimase).




## Meeskond ja Tööjaotus

| Roll | Vastutus | Täitja |
|---|---|---|
| Andmeallika omanik | Kontrollib API vastust ja kirjutab sissevõtu loogika | Oliver Soom |
| Transformatsioonide omanik | Kirjutab ja hooldab dbt mudeleid | Marika Eik |
| Kvaliteedi omanik | Kirjutab testid ja vaatab läbi ebaõnnestunud kontrollid | Katrin Toe |
| Näidikulaua omanik | Ehitab Superset chart'e ja dashboardi | Carola Kesküla |


## Riskid

| Risk | Mõju | Maandus |
|---|---|---|
| API ei vasta või võrgupäring ebaõnnestub | Andmeid ei saa värskendada | Skript annab selge veateate; käivitamine kordub järgmisel tunnil automaatselt. |
| API väljade nimed muutuvad | Laadimine katkeb | Testides kontrollitakse nõutud väljade olemasolu. |
| Ei õnnestu compose failist panna kogu toolingut püsti | Rakenduskeskkond ei käivitu või osa teenuseid ei tööta |  Kasutatakse eraldi compose profiile ja teenuseid testitakse ükshaaval; probleemide korral saab komponendid käivitada ka lokaalselt. |
| Dashboard näitab vanu andmeid | Andmed on ebakorrektsed | Dashboardil kuvatakse viimase laadimise aeg. |
| Superset init aeglane | Esimesel käivitusel tuleb oodata 2-3 minutit | Docker Compose ei seadista automaatselt Superset'i valmisoleku kontrolli (healthcheck’i) — kontrollitakse konteinerite logisid enne ühendamist. |
| Ei saa projekti õigeks ajaks täies mahus valmis | | Alustada arendusega juba esimesel nädalal. |

## Privaatsus ja turve

Projekt kasutab ainult avalikke lennuandmeid. Isikuandmeid ei koguta. Andmebaasi kasutajanimi ja parool tulevad `.env` failist. Päris `.env` faili ei tohi reposse lisada.

---

## 1 Enne alustamist tuleb luua Docker konteineri teenused:

### Kuidas käivitada:
```
docker compose build --no-cache
docker compose up -d
```

### Konkreetse Docker konteineri teenuse sisse/ välja lülitamine:
```
docker compose build --no-cache <service_name>
docker compose up -d <service_name>

docker compose stop <service_name>
```

### Keskkonnamuutujad ja sõltuvused

<details>
<summary>Keskkonnamuutujad</summary>

#### pgduckdb
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_DB


#### dbt
- (no direct environment variables defined)


#### superset_db; Superseti metaandmete baas (eraldi postgres konteiner)
- SUPERSET_DB_USER
- SUPERSET_DB_PASSWORD
- SUPERSET_DB_NAME


#### Superseti rakenduse seaded
- SUPERSET_SECRET_KEY
- SUPERSET_ADMIN_USER
- SUPERSET_ADMIN_PASSWORD
- SUPERSET_ADMIN_EMAIL
</details>


<details>
<summary>Teenuse sõltuvused</summary>

#### python
- pgduckdb

#### superset
- superset-init (service_completed_successfully)

#### superset-init
- superset_db (service_started)

#### dbt
- pgduckdb
</details>


## 2 Andmete pärimine ja laadimine, dbt-mudelite loomine: silver, mart


* Raw tasemel andmeid kasutatakse dbt-mudelite ehitamiseks: ...;

* Mart taseme andmeid, st ./mart/fact_*, kasutatakse ülesannetes: SuperSet.

* dbt-utils paketi installimiseks lisa dbt-projekti packages.yml faili ja käivita dbt deps


```packages.yml
packages:
  - package: dbt-labs/dbt_utils
    version: [">=1.1.0", "<2.0.0"]
```

```bash
docker exec dbt dbt deps
```

* dbt-projekti dokumentatsiooni saab genereerida järgmiselt:

```
docker exec dbt dbt docs generate
```
and/or be found in:

```
/dbt/target/catalog.json
```


### 2.1 Laadi andmed API-st PostgreSQL-i.


```bash
docker compose exec python python opensky_ingest.py --days 30
docker compose exec python python ingest.py
#
# docker compose exec python python ingest.py users
# docker compose exec python python ingest.py posts --batch 1
# docker compose exec python python ingest.py posts --batch 2
```
Kontrolli tulemust:

```bash
docker exec -it lennujaam_db psql -U lennujaam -d lennujaam_db
```

```sql
\dn

\dt staging.*

```
```bash
docker exec -it lennujaam_db psql -U lennujaam -d lennujaam_db -c "SELECT COUNT(*) FROM staging.arrivals;"
docker exec -it lennujaam_db psql -U lennujaam -d lennujaam_db -c "SELECT COUNT(*) FROM staging.departures;"
```

### 2.2 Käivita dbt mudelid ja testid

* dbt-projekti täielikuks värskendamiseks ja paketide re-installimiseks, jooksuta:
```bash
docker compose exec dbt dbt clean
docker compose exec dbt dbt deps
```

* Käivita `seeds`. `dbt` laeb kõik `seeds/` kataloogist leitud CSV-failid andmebaasi:`public_staging.airports`. Esmalt veenduge Veenduge, et `dbt` näeb `/seeds`.

```bash
docker compose exec dbt dbt ls --resource-type seed
docker compose exec dbt dbt seed
```

* Käivita dbt mudelid ja testid
```bash
docker compose exec dbt dbt build
docker compose exec dbt dbt docs generate
```
* Käivita dbt metadata (Hetkel ei töötanud; aga ma sätin seda (Meik))
```bash
docker compose exec dbt dbt docs generate
```

## 3 Superset dashboardi importimine:

1. Ava Superset: http://localhost:8088
2. Impordi dashboard ZIP:
   - **Dashboards** (vasakult esimene menüüelement) -> otsi paremalt ülevalt impordiikooni (Bulk Select nupust vasakul) - Import Dashboards. Vajuta sellele. 
   - Vali imporditav fail: `superset/exports/dashboard_export_*.zip` (nt `dashboard_export_20260529T180446.zip`)
   - Avanenud aken küsib ka PostgreSQL.yaml parooli. 
   Sisesta .env failist POSTGRES_PASSWORD.
3. Ava dashboard nimega **Lennujaama tiimi dashboard**:

![Lennujaama tiimi dashboard Supersetis](/images/initial_superset_dashboard.png)

---
---
---

## Varia ajutised lisad:

## 6. Create Roles, Views in pgduckdb

### Create Users and Roles

The user and role configuration is located in `sql/user_management/create_users_and_roles.sql`. This script:
- Creates two users: `analyst_limited` and `analyst_full`
- Creates two roles: `limited` and `full`
- Assigns roles to their respective users
- Grants necessary table access to each role

Run this script first:
```sql
clickhouse-client < sql/user_management/create_users_and_roles.sql
```

### Create Views

After setting up roles, create the views by running `sql/create_views.sql`. This script creates:
- **Masked views** (for `limited` role);
- **Unmasked views** (for `full` role).

The `limited` role is automatically granted access to the masked views.
```sql
clickhouse-client < sql/create_views.sql
```

### Users and Permissions

| User | Role | Access |
|------|------|--------|
| `analyst_full` | `full` | All tables and unmasked views |
| `analyst_limited` | `limited` | Masked views only |

### Images

Daily traffic view without masking accessed by full role:

![Daily traffic view without masking accessed by full role](/images/user_management/daily_traffic_full-full.png)

Daily traffic view without masking accessed by limited role:

![Daily traffic view without masking accessed by limited role](/images/user_management/daily_traffic_full-limited.png)

Summarized traffic view with masking accessed by full role

![Summarized traffic view with masking accessed by full role](/images/user_management/summarized_traffic_limited-full.png)

Summarized traffic view with masking accessed by limited role

![Summarized traffic view with masking accessed by limited role](/images/user_management/summarized_traffic_limited-limited.png)

There are a few more pictures/screenshots that are not included here (in the README).


## 8. SuperSet
For making the Superset docker-init.sh file executable, one should change the following (applies for Unix system users)
```bash

chmod +x docker/docker-init.sh
chmod +x docker/docker-bootstrap.sh
```

Then open Superset in your browser:

- URL: <http://localhost:8088>

###  Create a Superset service account

Create a service account in ClickHouse for Superset application.
It should have SELECT rights on "default_gold" schema.

```sql
CREATE ROLE role_superset_full;

CREATE USER peopletraffic_user IDENTIFIED WITH sha256_password BY 'peopletraffic_pass';

GRANT role_superset_full TO peopletraffic_user;

GRANT SELECT ON default_gold.* TO role_superset_full;

```
While connecting to SuperSet and selecting the connection type: ClickHouse;
```
host: clickhouse-server
port: 8123

user: peopletraffic_user
password: peopletraffic_pass
```## 7. OpenMetaData (OMD)

To access OpenMetadata
<http://localhost:8585/>
Username and password are in .env file.

Create a Clickhouse user for OpenMetadata. From Clickhouse UI:
```bash
CREATE ROLE role_openmetadata;

CREATE USER service_openmetadata IDENTIFIED WITH sha256_password BY 'omd_very_secret_password';

GRANT role_openmetadata TO service_openmetadata;

GRANT SELECT, SHOW ON system.* to role_openmetadata;

GRANT SELECT ON default_gold.* TO role_openmetadata;
```
Create Clickhouse service for OMD. From OMD UI:

```bash
Go to Settings → Services → Databases
Click + Add New Service
Choose ClickHouse as the service type
Fill in the connection details (adapt as needed):
Service Name: clickhouse_warehouse, can be whatever
Host and Port: clickhouse-server-omd:8123
Username: service_openmetadata
Password: omd_very_secret_password
Database: default_gold
Schema: leave empty
Https / Secure: leave off
Click Test Connection
If successful, click Next and Save the service.
```

It might be necessary to add Airflow user.
If you get Airflow error in OMD "Failed to connect to Airflow due to java.net.ConnectException. Is the host available at http://ingestion:8080"

Then create user:
```bash
docker exec -it openmetadata_mysql mysql -u root -ppassword
```

```bash
CREATE USER 'airflow_user'@'%' IDENTIFIED BY 'airflow_pass';
GRANT ALL PRIVILEGES ON airflow_db.* TO 'airflow_user'@'%';
FLUSH PRIVILEGES;
```
NB! OMD service can work differently on windows and other OS. If needed, please make necessary changes in compose file for your operating system.

![OMD images](/images/column_description.png)
![OMD images](/images/OMD_table_descriptions.png)
![OMD images](/images/added_test_cases.png)
![OMD images](/images/test_outcome.png)


### Superset Dashboard visibility in OMD_table_descriptions
![SupersetDB visibility in OMD](/images/omd_supersetdb_connection.png)
![SupersetDB visibility in OMD](/images/OMD_superset_con_agent.png)



###  Superset example Datasets can be created, such as:
Dataset from SQL

```sql
SELECT
    building_name,
    SUM(people_in) AS total_people_in,
    anyHeavy(toHour(join_timestamp)) AS mode_hour,
    anyHeavy(prcp) AS mode_prcp
FROM default_gold.fact_people_traffic
WHERE prcp != 0
  AND toMonth(join_timestamp) = 9  -- only September
GROUP BY building_name
ORDER BY building_name
LIMIT 1000;


SELECT
    building_name,
    toStartOfWeek(join_timestamp) AS week_start,  -- start of the week
    anyHeavy(prcp) AS mode_prcp,                  -- statistical mode of prcp within that week & building
    SUM(people_in) AS total_people_in
FROM default_gold.fact_people_traffic
WHERE prcp != 0
GROUP BY building_name, week_start
ORDER BY mode_prcp DESC, building_name DESC, week_start DESC
LIMIT 1000;

```

![SeperSet Dashboard answering the BQ-1 and BQ-2](/images/dashboard.png)

