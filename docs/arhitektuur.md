# Arhitektuur

## Äriküsimus

Millised on Tallinna lennujaama populaarseimad marsruudid nädala lõikes ja kuidas muutub lennuliiklus nädalapäevade lõikes?

## Mõõdikud

1. Top 10 sihtkohta ja lähtekohta nädalas
2. Nädalamuster — mis päevadel on kõige rohkem lende
3. Tipp-tunnid nädalas
4. Unikaalsed sihtkohad nädalas


## Andmeallikad

| Allikas | Tüüp | Muutuvus ajas | Kasutus |
|---|---|---|---|
| [OpenSky API](https://openskynetwork.github.io/opensky-api/rest.html) | Avalik HTTP API | Uueneb kord päevas | Põhiandmevoog |
| [OurAirports CSV](https://ourairports.com/help/data-dictionary.html) | CSV | Ei, staatiline | Lennujaama linna nimi ja riik |

Põhiandmevoog tuleb OpenSky API-st (endpointid: `GET /fligths/arrival` ja `GET /flights/departure`). 
Staatilisest lennujaama nimetuste CSV-st võetakse linna nimi ja riik.

## Andmevoog

draw.io pilt

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
