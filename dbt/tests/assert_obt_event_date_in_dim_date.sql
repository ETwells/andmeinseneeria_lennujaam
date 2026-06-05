-- Iga sündmuse kuupäev (event_date) peab leiduma dim_date dimensioonis.
-- Kui kuupäev puudub dim_date'ist, jääb liitmine (join) poolikuks ja tuletatud väljad
-- (year, month_name, weekday_name jne) tulevad NULL-iks.
-- Test läbib, kui päring tagastab 0 rida.

SELECT
    obt.event_date
FROM {{ ref('OBT_TLL_arrivals_departures') }} AS obt
LEFT JOIN {{ ref('dim_date') }} AS dd
    ON dd.full_date = obt.event_date
WHERE obt.event_date IS NOT NULL
  AND dd.full_date IS NULL
