# TALLINNA LENNUJAAMA MARSRUUTIDE UURING
<!--[GRUPI NIMI] — [PROJEKTI PEALKIRI]-->

> **Juhend:** Asenda kõik nurksulgudes vormid oma sisuga enne esitamist. Kustuta see juhendrida.

## Äriküsimus
<!--[Kirjelda ühe-kahe lausega, millise andmetega seotud probleemi te lahendate ja kes sellest kasu saab.]-->
Millised on Tallinna lennujaama populaarseimad marsruudid nädala lõikes ja kuidas muutub lennuliiklus nädalapäevade lõikes?

> Täpsustus: "populaarseim marsruut" tähendab antud projektis suurimat lennusündmuste arvu, mitte reisijate arvu.



**Mõõdikud:**
<!--1. [Esimene KPI või mõõdik — näiteks: päevane müük poe kohta]
2. [Teine KPI või mõõdik]
3. [Kolmas KPI või mõõdik — vabatahtlik]-->

1. **KPI-1: Top 10 sihtkohta ja lähtekohta nädalas** — kõige rohkem lende Tallinna lennujaama ja teise lennujaama vahel;
2. **KPI-2: Nädalamuster** — mis päevadel on kõige rohkem lende;
3. **KPI-3: Tipp-tunnid nädalas** — millistel kellaaegadel on Tallinna lennujaamas kõige rohkem saabumisi ja väljumisi;
4. **KPI-4: Unikaalsed sihtkohad nädalas** — mitme erineva lennujaamaga oli ühendus.


## Arhitektuur
<!--
Täpsem kirjeldus: [`docs/arhitektuur.md`](docs/arhitektuur.md)-->

![Dataflow architecture and tooling](/images/Lennujaam_ver3.jpg)


## Andmestik
<!--
| Allikas | Tüüp | Ajas muutuv? | Roll |
|---------|------|--------------|------|
| [Andmeallika nimi] | [API / fail / andmebaas] | Jah, [iga tund / päevas / muu] | Põhiandmevoog |
| [Teise allika nimi] | [seed / dim-tabel] | Ei, staatiline | Kõrvaltabel |-->

| Allikas | Tüüp | Muutuvus ajas | Kasutus |
|---|---|---|---|
| [OpenSky API](https://openskynetwork.github.io/opensky-api/rest.html) | Avalik HTTP API | Uueneb kord päevas öise batch-processiga | Põhiandmevoog: Tallinna lennujaama saabumised ja väljumised |
| [OurAirports CSV](https://ourairports.com/help/data-dictionary.html) | CSV/ dbt seed | Uuendatakse kord kuus | Lennujaama nimi ja kood ning linna nimi ja riik |

Põhiandmevoog tuleb OpenSky API-st (endpointid: `GET /flights/arrival` ja `GET /flights/departure`). Päringutes kasutatakse Tallinna lennujaama ICAO koodi `EETN`.

Staatilisest lennujaama nimetuste CSV-st võetakse lennujaama nimi ja kood ning linna nimi ja riik.


## Stack

| Komponent | Tööriist |
|-----------|---------|
| Sissevõtt | [Python / cron ] |
| Transformatsioon | [SQL / dbt ] |
| Andmehoidla | PostgreSQL |
| Näidikulaud | [Superset] |
| Orkestreerimine | [cron] |



## Käivitamine
```bash
# 1. Klooni repo ja liigu kausta
git clone <repo-url>
cd <projekti-kaust>

# 2. Kopeeri keskkonnamuutujad
cp .env.example .env
# Muuda .env failis paroolid ja muud seaded vastavalt vajadusele
```

Enne alustamist tuleb käivitada Docker konteineri teenused.

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

<!--### [Vabatahtlik: käivita sissevõtt käsitsi esimesel korral]
```
docker compose exec pipeline python scripts/run_pipeline.py run-all
```-->

## Saladused ja konfiguratsioon

<!--Kõik saladused (paroolid, API võtmed, andmebaasi URL-id) on `.env` failis. Repos on ainult `.env.example`, mis näitab vajalike muutujate struktuuri ilma tegelike väärtusteta. Päris `.env` faili ei tohi GitHubi panna - see on `.gitignore`-s.-->

Projekt kasutab ainult avalikke lennuandmeid. Isikuandmeid ei koguta. Andmebaasi kasutajanimi ja parool tulevad `.env` failist. Päris `.env` faili ei tohi/ei ole reposse lisatud.

<!--Vajalikud muutujad:

| Muutuja | Tähendus | Näide |
|---------|----------|-------|
| `DB_PASSWORD` | PostgreSQL parool | (saladus) |
| `[teised]` | ... | ... |-->


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


## Andmevoog lühidalt

1. **Andmete Orkestreerimine ja Sissevõtt** <!--— [Kirjelda, kuidas andmed allikast kätte saadakse]-->
<!--#### 2.1.1 Andmete orkestreerimine-->

Antud projekti puhul toimub andmete orkestreerimine: sissevõtt ning transformatsioon läbi cron'i tööde. Cron käivitatakse juurmasinas.
Cron'i tööde lisamiseks avada crontab:
```bash
crontab -e
```
Ja lisada järgnevad graafikud:

* Põhiandmete voog (Opensky API) Kord ööpäevas
```bash
0 3 * * * /opt/homebrew/bin/docker exec lennujaam-ingest python opensky_ingest.py >> $HOME/logs/lennujaam/ingest.log 2>&1
```
* andmete transformatsioon (dbt)
```bash
30 3 * * * /opt/homebrew/bin/docker exec lennujaam-dbt dbt build >> $HOME/logs/lennujaam/dbt.log 2>&1
```
* Lisaandmete voog (OurAirports CSV) Kord kuus
```bash
0 2 1 * * /opt/homebrew/bin/docker exec lennujaam-ingest python ingest.py >> $HOME/logs/lennujaam/seed.log 2>&1
```

2. **Laadimine** — Andmed laaditakse `staging` kihti kasutades Python failis defineeritud protseduure: API-st andmete pärimine, `lennujaam_db` PostgreSQL andmebaasi ja tabelite loomine.  Iga töövoo käivitus saab uue `run_id`. Vanad API vastused jäävad `staging` kihti alles.

```bash
docker compose exec python python opensky_ingest.py --days 25
docker compose exec python python ingest.py
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

3. **Andmebaasi kihid; Transformatsioon: dbt mudelid ja testid** <!--— [Kirjelda peamised arvutused ja mudelid]-->
<!--### Andmebaasi kihid-->

| Kiht | Roll |
|---|---|
| `seeds` | Hoiab staatilist andmekogumid, mida salvestatakse projekti sees .csv-failina ja laaditakse andmelattu tabelina. |
| `staging` | Hoiab API-st saadud lendude infot võimalikult allikalähedaselt |
| `silver` | Puhastatud ja rikastatud lennuandmed |
| `marts` | Agregeeritud andmed Superset'i jaoks |


`seeds` on ette nähtud viiteandmete jaoks, milleks on lennujaama nimi ja kood ning linna nimi ja riik.

`staging` kiht on peegeldus toorandmestikust, mida päritakse openSky API-st.

`silver` kihis tehakse eelmodifikatsioone, st filtreerimine, kohaliku Eesti ajavööndiga arvestamine, tabelite basic JOINS `seeds`-is oleva viitetabeliga. Samuti defineeritakse lennujaama vaste kinnituste astmed, näiteks: `Airport Match Confirmed`.

`marts` tabelid esitavad `OBT`' andmemudelit ning on ettenähtud püstitatud äriküsimusele vastamiseks läbi defineeritud KPI-de. Samuti `marts` tabelid sisaldavad kõigi käivituste andmeid (Superset filtreerib viimase).
Antud projektis `marts` kiht on rikastatud `dim_date` ja `dim_time` dimensioonidega, et võimaldada lendude jälgimise võimaluse ajateljest lähtuvalt. `OBT` tabel ühendab eelneva kihi, st `silver`, tabeleid ja lisaks  erinevaid ajalisi metrikuid, nagu näiteks `is_working_day`.


* dbt-utils paketi installimiseks lisa dbt-projekti `packages.yml` faili ja käivita dbt deps.
dbt_utils pakub lisaks sisseehitatud dbt-testidele mitmeid lisa andmekvaliteedi teste.

```packages.yml
packages:
  - package: dbt-labs/dbt_utils
    version: [">=1.1.0", "<2.0.0"]
```

* dbt-projekti täielikuks värskendamiseks ja paketide re-installimiseks, jooksuta:
```bash
docker compose exec dbt dbt clean
docker compose exec dbt dbt deps
```

* Käivita `seeds`. `dbt` laeb kõik `seeds/` kataloogist leitud CSV-failid andmebaasi:`public_staging.airports`. Esmalt veenduge, et `dbt` näeb `/seeds`.

```bash
docker compose exec dbt dbt ls --resource-type seed
docker compose exec dbt dbt seed
```

* Käivita dbt mudelid ja testid
```bash
docker compose exec dbt dbt build
docker compose exec dbt dbt test
```
* Käivita dbt metadata.
```bash
docker compose exec dbt dbt docs generate
```
Metadata failid on leitavad:
```
/dbt/target/catalog.json manifest.json run_results.json

```

4. **Testimine** <!--— [Mitu] andmekvaliteedi testi kontrollivad korrektsust-->

<!--## 4 Andmekvaliteedi testid-->

<!--Projekt kontrollib järgmist:

1. [Test 1 - nt: kasutajate ID on unikaalne]
2. [Test 2 - nt: tellimuse summa pole null]
3. [Test 3 - nt: kuupäev jääb vahemikku 2020-2026]
[Lisa rohkem, kui sul on]

Testide tulemused: [kuhu salvestatakse / kuidas vaadata]-->

Üldised testid (`not_null`, `unique`, `accepted_values`, `relationships`, `dbt_utils.*`) on kirjeldatud mudelite juures `schema.yml` / `models.yml` failides.

Projekti äriloogika testid:

1. **Test 1** Nädalavahetus või riigipüha ei tohi olla tööpäev.
2. **Test 2** Päevaosad (is_morning, is_afternoon, is_evening, is_night) peavad katma kogu ööpäeva ega tohi omavahel kattuda.
3. **Test 3** Iga sündmuse kuupäev (event_date) peab leiduma dim_date dimensioonis.
4. **Test 4** Lennu lähte- ja sihtlennujaam ei tohi olla samad.
5. **Test 5** Iga OBT faktitabeli rida peab olema seotud Tallinna lennujaamaga (TLL).
6. **Test 6** Saabuva lennu *last_seen* ei saa olla varem kui *first_seen*.
7. **Test 7** Väljuva lennu *last_seen* ei saa olla varem kui *first_seen*.

Kuna `dbt_project.yml` failis on `data_tests: +store_failures: true`, salvestatakse iga ebaõnnestunud testi read eraldi tabelisse (skeem `*_dbt_test__audit`), kus neid saab järelkontrolliks vaadata.

```bash
# Vaata ebaõnnestunud testide salvestatud ridu (store_failures)
docker exec lennujaam_db psql -U lennujaam -d lennujaam_db -c "\dt public_dbt_test__audit.*"
```

Testide käivitamine: vaata [dbt/tests/README.md](https://github.com/ETwells/andmeinseneeria_lennujaam/blob/main/dbt/tests/README.md)



5. **Näidikulaud** <!--— [Kirjelda lühidalt, mida näidikulaud näitab]-->

<!--## 3 Superset dashboardi importimine:-->

* Ava Superset: http://localhost:8088
* Impordi dashboard ZIP:
   - **Dashboards** (vasakult esimene menüüelement) -> otsi paremalt ülevalt impordiikooni (Bulk Select nupust vasakul) - Import Dashboards. Vajuta sellele.
   - Vali imporditav fail: `superset/exports/dashboard_export_*.zip` (nt `dashboard_export_20260529T180446.zip`)
   - Avanenud aken küsib ka PostgreSQL.yaml parooli.
   Sisesta .env failist POSTGRES_PASSWORD.
* Ava dashboard nimega **Lennujaama tiimi dashboard**:

![Lennujaama tiimi dashboard Supersetis](/images/initial_superset_dashboard.png)


## Projekti struktuur

```
├── compose.yml
├── data
├── dbt
│   ├── dbt_packages
│   │   └── dbt_utils
│   ├── dbt_project.yml
│   ├── logs
│   ├── models
│   │   ├── marts
│   │   ├── silver
│   │   └── sources.yml
│   ├── package-lock.yml
│   ├── packages.yml
│   ├── profiles.yml
│   ├── seeds
│   │   ├── airports.csv
│   │   └── schema.yml
│   ├── target
│   │   ├── catalog.json
│   │   ├── compiled
│   │   ├── graph.gpickle
│   │   ├── graph_summary.json
│   │   ├── index.html
│   │   ├── manifest.json
│   │   ├── partial_parse.msgpack
│   │   ├── run
│   │   ├── run_results.json
│   │   └── semantic_manifest.json
│   └── tests
│       ├── assert_dim_date_holiday_not_working_day.sql
│       ├── assert_dim_time_exactly_one_daypart.sql
│       ├── assert_obt_event_date_in_dim_date.sql
│       ├── assert_obt_no_self_loop.sql
│       ├── assert_obt_tll_involvement.sql
│       ├── assert_silver_arrivals_seen_order.sql
│       ├── assert_silver_departures_seen_order.sql
│       └── README.md
├── Dockerfile.dbt
├── Dockerfile.python
├── Dockerfile.superset
├── docs
│   ├── arhitektuur.md
│   └── progress.md
├── images
│   ├── initial_superset_dashboard.png
│   └── Lennujaam_ver3.jpg
├── README.md
├── scripts
│   ├── ingest.py
│   ├── opensky_ingest.py
│   └── requirements.txt
├── superset
│   ├── exports
│   │   └── dashboard_export_20260529T180446.zip
│   └── sql
│       ├── flights_by_hour.sql
│       └── flights_by_weekday.sql
└── superset_config.py
```

## Kokkuvõte, puudused ja võimalikud edasiarendused

**Kokkuvõte, Reflektsioon**
<!--- [Loetle, mis on lõpule viidud, mis töötab hästi]-->
* Oliver:

* Marika: Dockeris teenuste käivitamisel ilmnes dbt ja `Postgres` versioonide vastuolu. `dbt-core 2.0.0-alpha.1` uuemal versioonil puudub 'postgres' adapter ('postgres' adapter is not yet supported by dbt Fusion). Seetõttu on Dockeri teenuste installimisel oluline pöörata erilist tähelepanu teenuste versioonide ühilduvusele.

* Carola:

* Katrin: ajaline surve.

* Varia: API kättesaamatu



**Puudused:**
<!--- [Loetle ausalt, mis jäi tegemata - see ei mõjuta hinnet negatiivselt, vaid aitab hinnata]-->
<!--## Riskid-->

| Risk | Mõju | Maandus |
|---|---|---|
| API ei vasta või võrgupäring ebaõnnestub | Andmeid ei saa värskendada | Skript annab selge veateate; käivitamine kordub järgmisel tunnil automaatselt. |
| API väljade nimed muutuvad | Laadimine katkeb | Testides kontrollitakse nõutud väljade olemasolu. |
| Ei õnnestu compose failist panna kogu toolingut püsti | Rakenduskeskkond ei käivitu või osa teenuseid ei tööta |  Kasutatakse eraldi compose profiile ja teenuseid testitakse ükshaaval; probleemide korral saab komponendid käivitada ka lokaalselt. |
| Dashboard näitab vanu andmeid | Andmed on ebakorrektsed | Dashboardil kuvatakse viimase laadimise aeg. |
| Superset init aeglane | Esimesel käivitusel tuleb oodata 2-3 minutit | Docker Compose ei seadista automaatselt Superset'i valmisoleku kontrolli (healthcheck’i) — kontrollitakse konteinerite logisid enne ühendamist. |
| Ei saa projekti õigeks ajaks täies mahus valmis | | Alustada arendusega juba esimesel nädalal. |


**Mis edasi:**
<!--- [Mida tahaksid edasi teha, kui aega oleks rohkem]-->

## Meeskond ja Tööjaotus

| Roll | Vastutus | Täitja |
|---|---|---|
| Andmeallika omanik | Kontrollib API vastust ja kirjutab sissevõtu loogika | Oliver Soom |
| Transformatsioonide omanik | Kirjutab ja hooldab dbt mudeleid | Marika Eik |
| Kvaliteedi omanik | Kirjutab testid ja vaatab läbi ebaõnnestunud kontrollid | Katrin Toe |
| Näidikulaua omanik | Ehitab Superset chart'e ja dashboardi | Carola Kesküla |



