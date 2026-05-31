SELECT
  t.hour,
  COUNT(*) AS flight_count
FROM (
  SELECT EXTRACT(HOUR FROM first_seen_est)::int AS flight_hour
  FROM public_silver.silver_dim_arrivals
  WHERE first_seen_est IS NOT NULL
  UNION ALL
  SELECT EXTRACT(HOUR FROM first_seen_est)::int
  FROM public_silver.silver_dim_departures
  WHERE first_seen_est IS NOT NULL
) f
JOIN (SELECT DISTINCT hour FROM public_marts.dim_time) t
  ON f.flight_hour = t.hour
GROUP BY t.hour
ORDER BY t.hour;