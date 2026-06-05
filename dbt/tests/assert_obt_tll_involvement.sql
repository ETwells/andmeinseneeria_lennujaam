-- Ärireegel: iga OBT faktitabeli rida peab olema seotud Tallinna lennujaamaga (TLL).
--   - direction = 'arrival_TLL'   => arrival_iata peab olema 'TLL'
--   - direction = 'departure_TLL' => departure_iata peab olema 'TLL'
-- Test läbib, kui päring tagastab 0 rida (ühtegi reeglit rikkuvat rida pole).

SELECT
    direction,
    departure_iata,
    arrival_iata
FROM {{ ref('OBT_TLL_arrivals_departures') }}
WHERE NOT (
        (direction = 'arrival_TLL'   AND arrival_iata   = 'TLL')
     OR (direction = 'departure_TLL' AND departure_iata = 'TLL')
)
