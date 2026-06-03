{{ config(
    materialized='table',
    on_schema_change='sync_all_columns'
) }}

WITH date_data AS (

    SELECT
        gs::date AS full_date
    FROM generate_series(
        DATE '1965-01-01',
        DATE '2050-12-31',
        INTERVAL '1 day'
    ) AS gs

)

SELECT
    to_char(full_date, 'YYYYMMDD') AS date_key,

    full_date,

    trim(to_char(full_date, 'Day')) AS weekday_name,

    extract(isodow FROM full_date) AS day_of_week_num,

    CASE
        WHEN extract(isodow FROM full_date) IN (6, 7)
        THEN TRUE ELSE FALSE
    END AS is_weekend,

    CASE
        WHEN to_char(full_date, 'MM-DD') IN (
            '01-01',
            '02-24',
            '05-01',
            '06-23',
            '06-24',
            '08-20',
            '12-24',
            '12-25',
            '12-26'
        )
        THEN TRUE ELSE FALSE
    END AS is_holiday,

    CASE
        WHEN extract(isodow FROM full_date) IN (6, 7)
          OR to_char(full_date, 'MM-DD') IN (
                '01-01',
                '02-24',
                '05-01',
                '06-23',
                '06-24',
                '08-20',
                '12-24',
                '12-25',
                '12-26'
          )
        THEN FALSE ELSE TRUE
    END AS is_working_day,

    extract(month FROM full_date) AS month,

    to_char(full_date, 'Month') AS month_name,

    extract(quarter FROM full_date) AS quarter,

    extract(year FROM full_date) AS year

FROM date_data

ORDER BY full_date
