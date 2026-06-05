{{ config(
    materialized='table',
    on_schema_change='sync_all_columns'
) }}

WITH arrivals_to_tll AS (

    SELECT
        'arrival_TLL' AS direction,

        a.last_seen_est AS event_timestamp,
        CAST(a.last_seen_est AS date) AS event_date,

        a.departure_iata,
        a.departure_icao,
        a.departure_airport_name,

        a.arrival_iata,
        a.arrival_icao,
        a.arrival_airport_name,

        a.loaded_at

    FROM {{ ref('silver_dim_arrivals') }} a

    WHERE a.arrival_iata = 'TLL'
      --AND a.arrival_airport_match_status = 'Airport Match Confirmed'

),

departures_from_tll AS (

    SELECT
        'departure_TLL' AS direction,

        d.first_seen_est AS event_timestamp,
        CAST(d.first_seen_est AS date) AS event_date,

        d.departure_iata,
        d.departure_icao,
        d.departure_airport_name,

        d.arrival_iata,
        d.arrival_icao,
        d.arrival_airport_name,

        d.loaded_at

    FROM {{ ref('silver_dim_departures') }} d

    WHERE d.departure_iata = 'TLL'
      AND d.arrival_airport_match_status = 'Airport Match Confirmed'

),

flights AS (

    SELECT *
    FROM arrivals_to_tll

    UNION ALL

    SELECT *
    FROM departures_from_tll

)

SELECT
    f.direction,

    -- f.event_timestamp,
    f.event_date,

    dd.month_name,
    dd.weekday_name,
    -- dd.day_of_week_num,
    dd.is_holiday,
    dd.is_working_day,
    -- dd.month,
    -- dd.quarter,
    dd.year,

    dt.hour,
    dt.is_morning,
    dt.is_afternoon,
    dt.is_evening,
    dt.is_night,
    -- dt.is_business_hours,

    f.departure_iata,
    f.departure_icao,
    f.departure_airport_name,

    f.arrival_iata,
    f.arrival_icao,
    f.arrival_airport_name,

    f.loaded_at

FROM flights f

LEFT JOIN {{ ref('dim_date') }} dd
    ON dd.full_date = f.event_date

LEFT JOIN {{ ref('dim_time') }} dt
    ON dt.full_time = date_trunc('minute', f.event_timestamp)::time

-- Jäta välja kohalikud/treeninglennud, mis väljuvad ja saabuvad samasse
-- lennujaama (nt Tallinn -> Tallinn). OBT kirjeldab marsruute Tallinna ja
-- TEISE lennujaama vahel, mistõttu sama lennujaama marsruut pole asjakohane.
-- IS DISTINCT FROM hoiab alles read, kus lähte- või sihtkoht on teadmata (NULL).
WHERE f.departure_icao IS DISTINCT FROM f.arrival_icao

ORDER BY
    f.event_timestamp
