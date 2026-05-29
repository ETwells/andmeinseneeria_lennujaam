{{ config(
    materialized='table',
    on_schema_change='sync_all_columns'
) }}

WITH time_data AS (

    SELECT
        gs::time AS full_time
    FROM generate_series(
        TIMESTAMP '2000-01-01 00:00:00',
        TIMESTAMP '2000-01-01 23:59:00',
        INTERVAL '1 minute'
    ) AS gs

)

SELECT
    to_char(full_time, 'HH24MI') AS time_key,

    full_time,

    extract(hour FROM full_time) AS hour,

    extract(minute FROM full_time) AS minute,

    to_char(full_time, 'HH24:MI') AS time_hhmm,

    CASE
        WHEN extract(hour FROM full_time) BETWEEN 6 AND 11
        THEN TRUE ELSE FALSE
    END AS is_morning,

    CASE
        WHEN extract(hour FROM full_time) BETWEEN 12 AND 17
        THEN TRUE ELSE FALSE
    END AS is_afternoon,

    CASE
        WHEN extract(hour FROM full_time) BETWEEN 18 AND 21
        THEN TRUE ELSE FALSE
    END AS is_evening,

    CASE
        WHEN extract(hour FROM full_time) >= 22
          OR extract(hour FROM full_time) <= 5
        THEN TRUE ELSE FALSE
    END AS is_night,

    CASE
        WHEN extract(hour FROM full_time) BETWEEN 9 AND 17
        THEN TRUE ELSE FALSE
    END AS is_business_hours

FROM time_data
ORDER BY full_time
