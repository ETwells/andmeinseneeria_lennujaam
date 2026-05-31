{{ config(
    materialized='view',
    on_schema_change='sync_all_columns'
) }}

WITH departures AS (

    SELECT *
    FROM {{ source('staging', 'departures') }}

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
    d.icao24,

    d.first_seen AS first_seen_utc,
    d.first_seen AT TIME ZONE 'Europe/Tallinn' AS first_seen_est,

    d.last_seen AS last_seen_utc,
    d.last_seen AT TIME ZONE 'Europe/Tallinn' AS last_seen_est,

    TRIM(d.callsign) AS callsign,

    d.est_departure_airport,

    dep.name AS departure_airport_name,
    dep.municipality AS departure_city,
    dep.iso_country AS departure_country,
    dep.iata AS departure_iata,
    dep.icao AS departure_icao,

    d.est_arrival_airport,

    arr.name AS arrival_airport_name,
    arr.municipality AS arrival_city,
    arr.iso_country AS arrival_country,
    arr.iata AS arrival_iata,
    arr.icao AS arrival_icao,

    d.est_departure_airport_horiz_dist,
    d.est_departure_airport_vert_dist,

    d.est_arrival_airport_horiz_dist,
    d.est_arrival_airport_vert_dist,

    d.departure_airport_candidates_count,

    CASE
        WHEN d.departure_airport_candidates_count = 0
            THEN 'Airport Match Confirmed'
        WHEN d.departure_airport_candidates_count <= 5
            THEN 'Likely Airport Match'
        WHEN d.departure_airport_candidates_count <= 20
            THEN 'Possible Airport Match'
        ELSE 'Airport Match Uncertain'
    END AS departure_airport_match_status,

    d.arrival_airport_candidates_count,

    CASE
        WHEN d.arrival_airport_candidates_count = 0
            THEN 'Airport Match Confirmed'
        WHEN d.arrival_airport_candidates_count <= 5
            THEN 'Likely Airport Match'
        WHEN d.arrival_airport_candidates_count <= 20
            THEN 'Possible Airport Match'
        ELSE 'Airport Match Uncertain'
    END AS arrival_airport_match_status,

    d.loaded_at

FROM departures AS d

LEFT JOIN airports AS dep
    ON d.est_departure_airport = dep.icao

LEFT JOIN airports AS arr
    ON d.est_arrival_airport = arr.icao
