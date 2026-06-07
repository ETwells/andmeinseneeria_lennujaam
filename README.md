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
│   ├── tests
│   └── target
├── Dockerfile.dbt
├── Dockerfile.python
├── Dockerfile.superset
├── docs
│   ├── arhitektuur.md
│   └── progress.md
├── README.md
├── superset
│   ├── dashboard_export_20260529T180446.zip
│   └── dashboard_export_20260607T132733.zip
├── scripts
│   ├── ingest.py
│   ├── opensky_ingest.py
│   └── requirements.txt
└── superset_config.py
```


## Äriküsimus

Millised on Tallinna lennujaama populaarseimad marsruudid nädala lõikes ja kuidas muutub lennuliiklus nädalapäevade lõikes?

> Täpsustus: "populaarseim marsruut" tähendab antud projektis suurimat lennusündmuste arvu, mitte reisijate arvu.

## Mõõdikud

1. **Top 10 sihtkohta ja lähtekohta nädalas** — kõige rohkem lende Tallinna lennujaama ja teise lennujaama vahel.
2. **Lendude arv iga nädalapäeva kohta** — mis päevadel on kõige rohkem lende.
3. **Tipp-tunnid nädalas** — millistel kellaaegadel on Tallinna lennujaamas kõige rohkem saabumisi ja väljumisi.
4. **Unikaalsed sihtkohad nädalas** — mitme erineva lennujaamaga oli ühendus.

## Andmestik: andmeallikad

| Allikas | Tüüp | Muutuvus ajas | Kasutus |
|---|---|---|---|
| [OpenSky API](https://openskynetwork.github.io/opensky-api/rest.html) | Avalik HTTP API | Uueneb kord päevas öise batch-processiga | Põhiandmevoog: Tallinna lennujaama saabumised ja väljumised |
| [OurAirports CSV](https://ourairports.com/help/data-dictionary.html) | CSV/ dbt seed | Uuendatakse kord kuus | Lennujaama nimi ja kood ning linna nimi ja riik |

Põhiandmevoog tuleb OpenSky API-st (endpointid: `GET /flights/arrival` ja `GET /flights/departure`). Päringutes kasutatakse Tallinna lennujaama ICAO koodi `EETN`.

Staatilisest lennujaama nimetuste CSV-st võetakse lennujaama nimi ja kood ning linna nimi ja riik.


## Arhitektuur

![Dataflow architecture and tooling](/images/Lennujaam_ver3.jpg)


<!--<img width="816" height="754" alt="image" src="https://github.com/user-attachments/assets/bc308b37-274f-4fbd-9b5e-9c362a071b1b" />-->

## Stack

| Komponent | Tööriist |
|-----------|---------|
| Sissevõtt | [Python / cron ] |
| Transformatsioon | [SQL / dbt ] |
| Andmehoidla | PostgreSQL |
| Näidikulaud | [Superset] |
| Orkestreerimine | [cron] |


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
#### 2.1.1 Andmete orkestreerimine

Antud projekti puhul toimub orkestreerimine ning andmete transformatsioon läbi cron'i tööde. Cron käivitatakse juurmasinas.
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
   - Vali imporditav fail (eelistatult kõige viimase kuupäevaga .zip): `superset/dashboard_export_*.zip` (nt `dashboard_export_20260607T132733.zip`)
   - Avanenud aken küsib ka PostgreSQL.yaml parooli. 
   Sisesta .env failist POSTGRES_PASSWORD.
3. Ava dashboard nimega **Lennujaama tiimi dashboard**:

![Lennujaama tiimi dashboard Supersetis](/images/final_superset_dashboard.png)


## 4 Andmekvaliteedi testid

Üldised testid (`not_null`, `unique`, `accepted_values`, `relationships`, `dbt_utils.*`) on kirjeldatud mudelite juures `schema.yml` / `models.yml` failides.

Projekti äriloogika testid:

1. Nädalavahetus või riigipüha ei tohi olla tööpäev.
2. Päevaosad (is_morning, is_afternoon, is_evening, is_night) peavad katma kogu ööpäeva ega tohi omavahel kattuda. 
3. Iga sündmuse kuupäev (event_date) peab leiduma dim_date dimensioonis.
4. Lennu lähte- ja sihtlennujaam ei tohi olla samad.
5. Iga OBT faktitabeli rida peab olema seotud Tallinna lennujaamaga (TLL).
6. Saabuva lennu *last_seen* ei saa olla varem kui *first_seen*. 
7. Väljuva lennu *last_seen* ei saa olla varem kui *first_seen*. 

Kuna `dbt_project.yml` failis on `data_tests: +store_failures: true`, salvestatakse iga ebaõnnestunud testi read eraldi tabelisse (skeem `*_dbt_test__audit`), kus neid saab järelkontrolliks vaadata.

```bash
# Vaata ebaõnnestunud testide salvestatud ridu (store_failures)
docker exec lennujaam_db psql -U lennujaam -d lennujaam_db -c "\dt public_dbt_test__audit.*"
```

Testide käivitamine: vaata [dbt/tests/README.md](https://github.com/ETwells/andmeinseneeria_lennujaam/blob/main/dbt/tests/README.md)

