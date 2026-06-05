-- Lendu ei saa olla viimati nähtud (last_seen) varem kui esmakordselt (first_seen).
-- Kontrollime saabumiste silver-mudelit.
-- Test läbib, kui päring tagastab 0 rida.

SELECT
    icao24,
    first_seen_utc,
    last_seen_utc
FROM {{ ref('silver_dim_arrivals') }}
WHERE last_seen_utc < first_seen_utc
