-- Lennu lähte- ja sihtlennujaam ei tohi olla samad.
-- Kontrollime ainult ridu, kus mõlemad ICAO koodid on teada.
-- Test läbib, kui päring tagastab 0 rida.

SELECT
    direction,
    departure_icao,
    arrival_icao
FROM {{ ref('OBT_TLL_arrivals_departures') }}
WHERE departure_icao IS NOT NULL
  AND arrival_icao IS NOT NULL
  AND departure_icao = arrival_icao
