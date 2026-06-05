-- Nädalavahetus või riigipüha ei tohi olla tööpäev.
-- St kui is_weekend või is_holiday on TRUE, peab is_working_day olema FALSE.
-- Test läbib, kui päring tagastab 0 rida.

SELECT
    full_date,
    is_weekend,
    is_holiday,
    is_working_day
FROM {{ ref('dim_date') }}
WHERE (is_weekend OR is_holiday)
  AND is_working_day