SELECT
  dow AS day_of_week,
  CASE dow
    WHEN 1 THEN '01 Esmaspäev'
    WHEN 2 THEN '02 Teisipäev'
    WHEN 3 THEN '03 Kolmapäev'
    WHEN 4 THEN '04 Neljapäev'
    WHEN 5 THEN '05 Reede'
    WHEN 6 THEN '06 Laupäev'
    WHEN 7 THEN '07 Pühapäev'
  END AS day_name,
  COUNT(*) AS flight_count
FROM (
  SELECT EXTRACT(ISODOW FROM first_seen_est)::int AS dow
  FROM public_silver.silver_dim_arrivals
  WHERE first_seen_est IS NOT NULL
  UNION ALL
  SELECT EXTRACT(ISODOW FROM first_seen_est)::int AS dow
  FROM public_silver.silver_dim_departures
  WHERE first_seen_est IS NOT NULL
) u
GROUP BY dow
ORDER BY dow;