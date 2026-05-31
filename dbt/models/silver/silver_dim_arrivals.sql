{{ config(
    materialized='view',
    on_schema_change='sync_all_columns'
) }}

WITH arrivals AS (

    SELECT *
    FROM {{ source('staging', 'arrivals') }}

),

airports AS (

    SELECT
        icao,
        iata,
        name,
        municipality,
        iso_country
    FROM {{ ref('airports') }}

)

SELECT
    a.icao24,

    a.first_seen AS first_seen_utc,
    a.first_seen AT TIME ZONE 'Europe/Tallinn' AS first_seen_est,

    a.last_seen AS last_seen_utc,
    a.last_seen AT TIME ZONE 'Europe/Tallinn' AS last_seen_est,

    TRIM(a.callsign) AS callsign,

    a.est_departure_airport,

    dep.name AS departure_airport_name,
    dep.municipality AS departure_city,
    dep.iso_country AS departure_country,
    dep.iata AS departure_iata,
    dep.icao AS departure_icao,

    a.est_arrival_airport,

    arr.name AS arrival_airport_name,
    arr.municipality AS arrival_city,
    arr.iso_country AS arrival_country,
    arr.iata AS arrival_iata,
    arr.icao AS arrival_icao,

    a.est_departure_airport_horiz_dist,
    a.est_departure_airport_vert_dist,

    a.est_arrival_airport_horiz_dist,
    a.est_arrival_airport_vert_dist,

    a.departure_airport_candidates_count,

    CASE
        WHEN a.departure_airport_candidates_count = 0
            THEN 'Airport Match Confirmed'
        WHEN a.departure_airport_candidates_count <= 5
            THEN 'Likely Airport Match'
        WHEN a.departure_airport_candidates_count <= 20
            THEN 'Possible Airport Match'
        ELSE 'Airport Match Uncertain'
    END AS departure_airport_match_status,

    a.arrival_airport_candidates_count,

    CASE
        WHEN a.arrival_airport_candidates_count = 0
            THEN 'Airport Match Confirmed'
        WHEN a.arrival_airport_candidates_count <= 5
            THEN 'Likely Airport Match'
        WHEN a.arrival_airport_candidates_count <= 20
            THEN 'Possible Airport Match'
        ELSE 'Airport Match Uncertain'
    END AS arrival_airport_match_status,

    a.loaded_at

FROM arrivals a

LEFT JOIN airports dep
    ON a.est_departure_airport = dep.icao

LEFT JOIN airports arr
    ON a.est_arrival_airport = arr.icao
