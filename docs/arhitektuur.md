# Arhitektuur

## Äriküsimus

Millised on Tallinna lennujaama populaarseimad marsruudid nädala lõikes ja kuidas muutub lennuliiklus nädalapäevade lõikes?

> Täpsustus: "populaarseim marsruut" tähendab antud projektis suurimat lennusündmuste arvu, mitte reisijate arvu.

## Mõõdikud

1. **KPI-1: Top 10 sihtkohta ja lähtekohta nädalas** — kõige rohkem lende Tallinna lennujaama ja teise lennujaama vahel;
2. **KPI-2: Lendude arv iga nädalapäeva kohta** — mis päevadel on kõige rohkem lende;
3. **KPI-3: Tipp-tunnid nädalas** — millistel kellaaegadel on Tallinna lennujaamas kõige rohkem saabumisi ja väljumisi;
4. **KPI-4: Unikaalsed sihtkohad nädalas** — mitme erineva lennujaamaga oli ühendus.


## Andmeallikad

| Allikas | Tüüp | Muutuvus ajas | Kasutus |
|---|---|---|---|
| [OpenSky API](https://openskynetwork.github.io/opensky-api/rest.html) | Avalik HTTP API | Uueneb kord päevas öise batch-processiga | Põhiandmevoog: Tallinna lennujaama saabumised ja väljumised |
| [OurAirports CSV](https://ourairports.com/help/data-dictionary.html) | CSV/ dbt seed | Ei, staatiline | Lennujaama nimi ja kood ning linna nimi ja riik |

Põhiandmevoog tuleb OpenSky API-st (endpointid: `GET /flights/arrival` ja `GET /flights/departure`). Päringutes kasutatakse Tallinna lennujaama ICAO koodi `EETN`.

Staatilisest lennujaama nimetuste CSV-st võetakse lennujaama nimi ja kood ning linna nimi ja riik.

## Andmevoog

![Dataflow architecture and tooling](/images/Lennujaam_ver3.jpg)

## Andmebaasi kihid

| Kiht | Roll |
|---|---|
| `staging` | Hoiab API-st saadud lendude infot võimalikult allikalähedaselt |
| `intermediate` | Puhastatud ja rikastatud lennuandmed |
| `marts` | Agregeeritud andmed Superset'i jaoks |

Iga töövoo käivitus saab uue `run_id`. Vanad API vastused jäävad `staging` kihti alles. `marts` tabelid sisaldavad kõigi käivituste andmeid (Superset filtreerib viimase).

## Tööjaotus

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
